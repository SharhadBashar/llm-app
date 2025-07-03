import os
import sys
import uuid
import asyncio
import aiohttp
import logfire

from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils import track_latency
from llms.factory import LLMFetcher
from db import get_db, BaseDBOperations
from utils.usage_tracker import UsageTracker
from core.summaries.helper import extract_source_data, get_backend_write_endpoint

from core.summaries.constants import SUMMARY_CONFIG
from core.summaries.serializers import Summaries_Request
from core.summaries.types import Source_Type, Tags, All_Tags
from core.summaries.models import Summaries as Summaries_Model

class Summaries:
    SESSION_ID = str(uuid.uuid4())[:5]
    def __init__(self):
        logfire.configure(token = os.environ.get('LOGFIRE_API_KEY'), service_name = self.SESSION_ID)
        logfire.instrument_openai()
        self.llm = LLMFetcher(provider = 'openai').async_client
        self.usage_tracker = UsageTracker()
        self.db = BaseDBOperations(Summaries_Model)
    
    @logfire.instrument(f'AI summary | {SESSION_ID}')
    async def generate(self, request: Summaries_Request) -> str | None:
        try:
            self.entity_id = request.entity_id
            self.entity_name = request.entity_name
            self.source_type = request.source_type
            self.source_ids, self.source_reviews = extract_source_data(request.sources)
            
            logfire.info(f'Initializing summary generation for supplier: {self.entity_id}, with {len(self.source_reviews)} reviews')
            summary, latency = await self._generate_summary()
            if summary:
                summary_id = await self._write_summary_to_ai_schema(self.entity_id, self.source_type, self.source_ids, summary, latency)
                await self._write_summary_to_public_schema(self.entity_id, summary)
                return summary_id
            else:
                logfire.warning(f'No summary generated for supplier: {self.entity_id}')
                return None
        except Exception as e:
            logfire.error(f'Error in {self.__class__.__name__}.{self.generate.__name__}: {e}')
            raise e
    
    async def _response(self, model: str, system_message: str, user_message: str) -> tuple[str, float]:
        try:
            response = await self.llm.responses.create(
                model = model,
                input = [
                    {'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': user_message}
                ]
            )
            return response.output_text, self.usage_tracker.get_responses_cost_simple(model, response.usage)
        except Exception as e:
            logfire.error(f'Error in {self.__class__.__name__}.{self._response.__name__}: {e}')
            raise e
    
    async def _response_structured_output(self, model: str, system_message: str, user_message: str, text_format) -> tuple[object, float]:
        try:
            response = await self.llm.responses.parse(
                model = model,
                input = [
                    {'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': user_message}
                ],
                text_format = text_format
            )
            return response.output_parsed, self.usage_tracker.get_responses_cost_simple(model, response.usage)
        except Exception as e:
            logfire.error(f'Error in {self.__class__.__name__}.{self._response_structured_output.__name__}: {e}')
            raise e
    
    @track_latency
    async def _generate_summary(self):
        async def _generate_summary_content():
            try:
                response_step_1, cost_step_1 = await self._response(
                    SUMMARY_CONFIG['step_1']['model'],
                    SUMMARY_CONFIG['step_1']['system_message'], 
                    f'Hotel name: {self.entity_name}, reviews: {self.source_reviews}'
                )
                response_step_2, cost_step_2 = await self._response(
                    SUMMARY_CONFIG['step_2']['model'],
                    SUMMARY_CONFIG['step_2']['system_message'], 
                    f'Hotel name: {self.entity_name}, reviews: {self.source_reviews}, summary: {response_step_1}'
                )
                return response_step_2, cost_step_1 + cost_step_2
            except Exception as e:
                logfire.error(f'Error in {self.__class__.__name__}.{self._generate_summary.__name__}.{_generate_summary_content.__name__}: {e}')
                raise e
        
        async def _generate_summary_tags():
            try:
                positive_tags_task = self._response_structured_output(
                    SUMMARY_CONFIG['positive_tags']['model'],
                    SUMMARY_CONFIG['positive_tags']['system_message'],
                    f'Hotel name: {self.entity_name}, reviews: {self.source_reviews}',
                    Tags
                )
                negative_tags_task = self._response_structured_output(
                    SUMMARY_CONFIG['negative_tags']['model'],
                    SUMMARY_CONFIG['negative_tags']['system_message'],
                    f'Hotel name: {self.entity_name}, reviews: {self.source_reviews}',
                    Tags
                )
                (positive_tags, cost_positive), (negative_tags, cost_negative) = await asyncio.gather(
                    positive_tags_task,
                    negative_tags_task
                )
                combined_tags, cost_combined = await self._response_structured_output(
                    SUMMARY_CONFIG['tags']['model'],
                    SUMMARY_CONFIG['tags']['system_message'],
                    f'Positive tags: {positive_tags.tags}, Negative tags: {negative_tags.tags}',
                    All_Tags
                )
                return combined_tags, cost_positive + cost_negative + cost_combined
            except Exception as e:
                logfire.error(f'Error in {self.__class__.__name__}.{self._generate_summary.__name__}.{_generate_summary_tags.__name__}: {e}')
                raise e
        try:
            summary_task = _generate_summary_content()
            tags_task = _generate_summary_tags()

            (summary, summary_cost), (tags, tags_cost) = await asyncio.gather(
                summary_task,
                tags_task
            )

            return {
                'summary': summary,
                'positive_tags': tags.positive_tags,
                'negative_tags': tags.negative_tags,
                'cost': round(summary_cost + tags_cost, 4)
            }
        except Exception as e:
            logfire.error(f'Error in {self.__class__.__name__}.{self._generate_summary.__name__}: {e}')
            raise e

    async def _write_summary_to_ai_schema(self, entity_id: str, source_type: Source_Type, sources: list[str], summary: dict, latency: float) -> str:
        try:
            with next(get_db()) as db:
                stored_content = self.db.create(db, {
                    'entity_id': entity_id,
                    'source_type': source_type.value,
                    'sources': sources,
                    'summary': summary['summary'],
                    'positive_tags': summary['positive_tags'],
                    'negative_tags': summary['negative_tags'],
                    'content_metadata': {
                        'logfire_session_id': self.SESSION_ID,
                        'cost': summary['cost'],
                        'latency': latency
                    }
                })
                logfire.info(f'Successfully wrote summary for supplier: {entity_id} to ai schema. Summary ID: {stored_content.id}')
                return str(stored_content.id)
        except Exception as e:
            logfire.error(f'Error in {self.__class__.__name__}.{self._write_summary_to_ai_schema.__name__}: {e}')
            raise e

    async def _write_summary_to_public_schema(self, entity_id: str, summary: dict):
        try:
            payload = {
                'supplier_id': str(entity_id),
                'summary': summary['summary'],
                'positive_tags': summary['positive_tags'],
                'negative_tags': summary['negative_tags']
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url = get_backend_write_endpoint(entity_id, self.source_type),
                    json = payload,
                    headers = {
                        'Content-Type': 'application/json',
                        'XAPIKEY': os.environ.get("FORA_PORTAL_BE_API_KEY")
                    },
                    timeout = aiohttp.ClientTimeout(total = 30)
                ) as response:
                    response.raise_for_status()
                    logfire.info(f'Successfully wrote summary for supplier: {entity_id} to public schema. Status: {response.status}')
        except KeyError as e:
            logfire.error(f'Invalid source type {self.source_type} in {self.__class__.__name__}.{self._write_summary_to_public_schema.__name__}: {e}')
            raise e
        except Exception as e:
            logfire.error(f'Error in {self.__class__.__name__}.{self._write_summary_to_public_schema.__name__}: {e}')
            raise e
