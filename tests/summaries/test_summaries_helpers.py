import os
import uuid
import pytest
import logfire
from unittest.mock import patch

from core.summaries.types import Source, Source_Type
from core.summaries.helper import extract_source_data, get_backend_write_endpoint

class Test_Summaries_Helpers:
    def test__extract_source_data__valid_sources(self):
        logfire.configure(send_to_logfire = False)
        source_id1 = uuid.uuid4()
        source_id2 = uuid.uuid4()
        sources = [
            Source(id = source_id1, review = 'Great hotel with excellent service'),
            Source(id = source_id2, review = 'Nice location but noisy rooms')
        ]
        
        ids, reviews = extract_source_data(sources)
        
        assert len(ids) == 2
        assert len(reviews) == 2
        assert source_id1 in ids
        assert source_id2 in ids
        assert 'Great hotel with excellent service' in reviews
        assert 'Nice location but noisy rooms' in reviews

    def test__get_backend_write_endpoint__valid_source_type(self):
        logfire.configure(send_to_logfire = False)
        entity_id = str(uuid.uuid4())
        with patch.dict(os.environ, {'RESTRICTED_BASE_URL': 'https://api.example.com'}):
            result = get_backend_write_endpoint(entity_id, Source_Type.CLIENT_SUPPLIER_REVIEWS)

            assert result == f'https://api.example.com/v1/suppliers/{entity_id}/client-reviews/summary/'

    def test__get_backend_write_endpoint__invalid_source_types(self):
        logfire.configure(send_to_logfire = False)
        entity_id = str(uuid.uuid4())
        invalid_source_type = 'random_string'
        with pytest.raises(KeyError) as exc_info:
            get_backend_write_endpoint(entity_id, invalid_source_type)
        
        assert exc_info.value.args[0] == f'{invalid_source_type} is not a valid source type.'
