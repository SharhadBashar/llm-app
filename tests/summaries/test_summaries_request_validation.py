import uuid
import pytest
import logfire
from pydantic import ValidationError

from core.summaries.serializers import Summaries_Request
from core.summaries.types import Source, Source_Type


class Test_Summaries_Request_Validation:
    def setup_method(self):
        logfire.configure(send_to_logfire = False)
        self.entity_id = uuid.uuid4()
        self.entity_name = 'Test Hotel'
        self.source_type = Source_Type.CLIENT_SUPPLIER_REVIEWS
        self.sources = [
            Source(id = uuid.uuid4(), review = 'Review 1'),
            Source(id = uuid.uuid4(), review = 'Review 2'),
            Source(id = uuid.uuid4(), review = 'Review 3')
        ]
    
    def test__valid_summaries_request(self):
        request = Summaries_Request(
            entity_id = self.entity_id,
            entity_name = self.entity_name,
            source_type = self.source_type,
            sources = self.sources
        )
        
        assert request.entity_id == self.entity_id
        assert request.entity_name == self.entity_name
        assert request.source_type == self.source_type
        assert len(request.sources) >= 3
    
    def test__invalid_summaries_request__missing_entity_id(self):
        with pytest.raises(ValidationError) as exc_info:
            Summaries_Request(
                entity_name = 'Test Hotel',
                source_type = self.source_type,
                sources = self.sources
            )
    
        assert 'entity_id' in str(exc_info.value)
        assert 'Field required' in str(exc_info.value)
    
    def test__invalid_summaries_request__missing_entity_name(self):
        with pytest.raises(ValidationError) as exc_info:
            Summaries_Request(
                entity_id = self.entity_id,
                source_type = self.source_type,
                sources = self.sources
            )
        assert 'entity_name' in str(exc_info.value)
        assert 'Field required' in str(exc_info.value)
    
    def test__invalid_summaries_request__less_than_3_sources(self):
        with pytest.raises(ValueError, match = 'At least 3 sources are required'):
            Summaries_Request(
                entity_id = self.entity_id,
                entity_name = self.entity_name,
                source_type = self.source_type,
                sources = self.sources[:2]
            )
    
    def test__invalid_summaries_request__no_sources(self):
        with pytest.raises(ValueError, match = 'At least 3 sources are required'):
            Summaries_Request(
                entity_id = self.entity_id,
                entity_name = self.entity_name,
                source_type = self.source_type,
                sources = []
            )
