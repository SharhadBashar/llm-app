import uuid
import pytest
import aiohttp
import logfire
from unittest.mock import patch
from aioresponses import aioresponses

from core.summaries.summaries import Summaries
from core.summaries.types import Source_Type


class Test_Write_Summary_To_Public_Schema:
    def setup_method(self):
        self.supplier_id = str(uuid.uuid4())
        self.base_url = 'http://test-url'
        self.api_key = 'test-api-key'

    @pytest.fixture
    def summaries_instance(self):
        logfire.configure(send_to_logfire = False)
        with patch('core.summaries.summaries.LLMFetcher'), \
             patch('core.summaries.summaries.UsageTracker'), \
             patch('core.summaries.summaries.BaseDBOperations'), \
             patch('core.summaries.summaries.logfire'):
            return Summaries()
    
    @pytest.fixture
    def mock_summary_data(self):
        return {
            'summary': 'Test hotel summary with positive and negative aspects',
            'positive_tags': ['clean', 'friendly staff', 'good location'],
            'negative_tags': ['noisy', 'expensive', 'small rooms']
        }
    
    @pytest.mark.asyncio
    async def test__write_summary_to_public_schema__success(self, summaries_instance, mock_summary_data):
        summaries_instance.entity_id = self.supplier_id
        summaries_instance.source_type = Source_Type.CLIENT_SUPPLIER_REVIEWS
        
        expected_url = f'{self.base_url}/v1/suppliers/{self.supplier_id}/client-reviews/summary/'
        
        expected_payload = {
            'supplier_id': self.supplier_id,
            'summary': mock_summary_data['summary'],
            'positive_tags': mock_summary_data['positive_tags'],
            'negative_tags': mock_summary_data['negative_tags']
        }
        
        with aioresponses() as m:
            m.post(expected_url, status = 201)
            
            with patch.dict('os.environ', {
                'RESTRICTED_BASE_URL': self.base_url,
                'FORA_PORTAL_BE_API_KEY': self.api_key
            }):
                await summaries_instance._write_summary_to_public_schema(self.supplier_id, mock_summary_data)
        
        request = list(m.requests.values())[0][0]
        assert request.kwargs['json'] == expected_payload
        assert request.kwargs['headers']['Content-Type'] == 'application/json'
        assert request.kwargs['headers']['XAPIKEY'] == self.api_key

        payload = request.kwargs['json']
        assert 'supplier_id' in payload
        assert 'summary' in payload
        assert 'positive_tags' in payload
        assert 'negative_tags' in payload
        assert payload['supplier_id'] == self.supplier_id
        assert isinstance(payload['positive_tags'], list)
        assert isinstance(payload['negative_tags'], list)
        
    @pytest.mark.asyncio
    async def test__write_summary_to_public_schema__error(self, summaries_instance, mock_summary_data):
        summaries_instance.entity_id = self.supplier_id
        summaries_instance.source_type = Source_Type.CLIENT_SUPPLIER_REVIEWS
        
        expected_url = f'{self.base_url}/v1/suppliers/{self.supplier_id}/client-reviews/summary/'
        
        with aioresponses() as m:
            m.post(expected_url, status = 500)
            
            with patch.dict('os.environ', {
                'RESTRICTED_BASE_URL': self.base_url,
                'FORA_PORTAL_BE_API_KEY': self.api_key
            }):
                with pytest.raises(aiohttp.ClientResponseError):
                    await summaries_instance._write_summary_to_public_schema(self.supplier_id, mock_summary_data)
    
    @pytest.mark.asyncio
    async def test__write_summary_to_public_schema__missing_env_vars(self, summaries_instance, mock_summary_data):
        summaries_instance.entity_id = self.supplier_id
        summaries_instance.source_type = Source_Type.CLIENT_SUPPLIER_REVIEWS
        
        expected_url = f'{self.base_url}/v1/suppliers/{self.supplier_id}/client-reviews/summary/'
        
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(Exception):
                await summaries_instance._write_summary_to_public_schema(self.supplier_id, mock_summary_data)
    
    @pytest.mark.asyncio
    async def test__write_summary_to_public_schema__empty_tags(self, summaries_instance):
        summaries_instance.entity_id = self.supplier_id
        summaries_instance.source_type = Source_Type.CLIENT_SUPPLIER_REVIEWS
        
        summary_data_empty_tags = {
            'summary': 'Test summary with no tags',
            'positive_tags': [],
            'negative_tags': None
        }
        
        expected_url = f'{self.base_url}/v1/suppliers/{self.supplier_id}/client-reviews/summary/'
        
        with aioresponses() as m:
            m.post(expected_url, status=200)
            
            with patch.dict('os.environ', {
                'RESTRICTED_BASE_URL': self.base_url,
                'FORA_PORTAL_BE_API_KEY': self.api_key
            }):
                await summaries_instance._write_summary_to_public_schema(self.supplier_id, summary_data_empty_tags)
        
        request = list(m.requests.values())[0][0]
        payload = request.kwargs['json']
        assert payload['positive_tags'] == []
        assert payload['negative_tags'] == None
