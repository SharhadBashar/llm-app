from uuid import UUID
from enum import Enum
from typing import List
from pydantic import BaseModel, Field

class Source(BaseModel):
    id: UUID
    review: str = Field(description = 'The review that will be used for summarization')

class Source_Type(Enum):
    CLIENT_SUPPLIER_REVIEWS = 'client_supplier_reviews'
    ADVISOR_SUPPLIER_REVIEWS = 'advisor_supplier_reviews'
    ADVISOR_REVIEWS = 'advisor_reviews'
    ADVISOR_BRAND_REVIEWS = 'advisor_brand_reviews'

class Summary(BaseModel):
    summary: str = Field(description = 'The summary')
    tags: List[str] = Field(default_factory = list, description = 'List of tags for the summary')

class Tags(BaseModel):
    tags: List[str] = Field(default_factory = list, description = 'List of tags for the summary')

class All_Tags(BaseModel):
    positive_tags: List[str] = Field(default_factory = list, description = 'List of positive tags for the summary')
    negative_tags: List[str] = Field(default_factory = list, description = 'List of negative tags for the summary')
