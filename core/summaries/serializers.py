import os
import logfire
from uuid import UUID
from pydantic import BaseModel, model_validator, field_validator

from core.summaries.types import Source
from core.summaries.types import Source_Type
from core.summaries.constants import MIN_SOURCES_FOR_SUMMARY

class Summaries_Request(BaseModel):
    entity_id: UUID
    entity_name: str
    source_type: Source_Type
    sources: list[Source]
    logfire.configure(token = os.environ.get('LOGFIRE_API_KEY'))

    @field_validator('entity_id', mode = 'before')
    @classmethod
    def validate_entity_id(cls, v):
        try:
            return UUID(str(v))
        except (ValueError, AttributeError) as e:
            logfire.error(f'entity_id: {v} is not a valid UUID', error = str(e))
            raise ValueError(f'Invalid UUID format: {v}')

    @model_validator(mode = 'after')
    def validate_request(self):
        if (len(self.sources) < MIN_SOURCES_FOR_SUMMARY):
            logfire.error(f'At least {MIN_SOURCES_FOR_SUMMARY} sources are required for {self.entity_id}, but only {len(self.sources)} were provided')
            raise ValueError(f'At least {MIN_SOURCES_FOR_SUMMARY} sources are required for {self.entity_id}, but only {len(self.sources)} were provided')
        return self
