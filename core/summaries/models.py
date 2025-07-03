import uuid
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy import Column, Text, DateTime, Enum, JSON

from db.base import Base
from core.summaries.types import Source_Type

class Summaries(Base):
    '''
        This table is used to store the summaries.
        Table name: summaries
        Schema: ai
        Columns:
            id: [UUID] - Primary key
            entity_id: [UUID] - The id of the entity that the summary is for (Suppliers, Advisors, etc.)
            source_type: [Enum] - The type of the source (Client Supplier Reviews, Advisor Supplier Reviews, etc.)
            sources: [ARRAY(UUID)] - The ids of whats used to generate the summary (Client Supplier Reviews, Advisor Supplier Reviews, etc.)
            summary: [Text] - The summary of the entity
            positive_tags: [ARRAY(Text)] - The positive tags of the summary
            negative_tags: [ARRAY(Text)] - The negative tags of the sumamry
            content_metadata: [JSON] - Other metadata (cost, latency, etc.)
            created_at: [DateTime]
            updated_at: [DateTime]
    '''
    __tablename__ = 'summaries'
    __table_args__ = {'schema': 'ai'}

    id = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    entity_id = Column(UUID(as_uuid = True), nullable = False)
    source_type = Column(Enum(
            Source_Type, 
            name = 'source_type', 
            schema = 'ai', 
            values_callable = lambda obj: [e.value for e in obj]
        ),
        nullable = False,
        default = Source_Type.CLIENT_SUPPLIER_REVIEWS
    )
    sources = Column(ARRAY(UUID(as_uuid = True)))
    summary = Column(Text, nullable = False)
    positive_tags = Column(ARRAY(Text))
    negative_tags = Column(ARRAY(Text))
    content_metadata = Column('metadata', JSON)
    created_at = Column(DateTime(timezone = True), server_default = func.now(), nullable = False)
    updated_at = Column(DateTime(timezone = True), server_default = func.now(), onupdate = func.now(), nullable = False)
