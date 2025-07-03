import os
import uuid
import pytest
import logfire
from unittest.mock import Mock, AsyncMock, patch

from core.summaries.summaries import Summaries
from core.summaries.types import Source_Type

class Test_Summaries_Write_To_AI_DB:
    @pytest.fixture
    def mock_summaries_for_write(self):
        logfire.configure(send_to_logfire = False)
        with patch('core.summaries.summaries.LLMFetcher') as mock_llm_fetcher, \
            patch('core.summaries.summaries.UsageTracker'), \
            patch('core.summaries.summaries.BaseDBOperations') as mock_db_ops, \
            patch('core.summaries.summaries.get_db') as mock_get_db, \
            patch('core.summaries.summaries.logfire'):  # Patch logfire to prevent actual logging
            
            mock_client = AsyncMock()
            mock_llm_fetcher.return_value.async_client = mock_client
            
            mock_db_session = Mock()
            mock_get_db.return_value.__next__.return_value = mock_db_session
            mock_get_db.return_value.__enter__ = Mock(return_value=mock_db_session)
            mock_get_db.return_value.__exit__ = Mock(return_value=None)
            
            mock_db_instance = Mock()
            mock_db_ops.return_value = mock_db_instance
            
            summaries = Summaries()
            
            summaries._mock_db_session = mock_db_session
            summaries._mock_db_instance = mock_db_instance
            
            return summaries
        
    @pytest.mark.asyncio
    async def test__write_summary_ai__success(self, mock_summaries_for_write):
        summaries = mock_summaries_for_write
        
        entity_id = str(uuid.uuid4())
        source_type = Source_Type.CLIENT_SUPPLIER_REVIEWS
        sources = [str(uuid.uuid4()), str(uuid.uuid4())]
        summary = {
            'summary': 'Great hotel with excellent service',
            'positive_tags': ['Location', 'Service', 'Cleanliness'],
            'negative_tags': ['Noise', 'Parking'],
            'cost': 0.0035
        }
        latency = 2.5
        
        mock_created_record = Mock()
        mock_created_record.id = uuid.uuid4()
        summaries.db.create.return_value = mock_created_record
        
        result = await summaries._write_summary_to_ai_schema(
            entity_id, source_type, sources, summary, latency
        )
        
        assert result == str(mock_created_record.id)
        
        summaries.db.create.assert_called_once()
        call_args = summaries.db.create.call_args
        
        data = call_args[0][1]
        assert data['entity_id'] == entity_id
        assert data['source_type'] == source_type.value
        assert data['sources'] == sources
        assert data['summary'] == 'Great hotel with excellent service'
        assert data['positive_tags'] == ['Location', 'Service', 'Cleanliness']
        assert data['negative_tags'] == ['Noise', 'Parking']
        assert data['content_metadata']['logfire_session_id'] == summaries.SESSION_ID
        assert data['content_metadata']['cost'] == 0.0035
        assert data['content_metadata']['latency'] == 2.5

    @pytest.mark.asyncio
    async def test__write_summary_ai__no_tags(self, mock_summaries_for_write):
        summaries = mock_summaries_for_write
        
        entity_id = str(uuid.uuid4())
        source_type = Source_Type.CLIENT_SUPPLIER_REVIEWS
        sources = [str(uuid.uuid4()), str(uuid.uuid4())]
        summary = {
            'summary': 'Great hotel with excellent service',
            'positive_tags': [],
            'negative_tags': [],
            'cost': 0.0035
        }
        latency = 2.5
        
        mock_created_record = Mock()
        mock_created_record.id = uuid.uuid4()
        summaries.db.create.return_value = mock_created_record
        
        result = await summaries._write_summary_to_ai_schema(
            entity_id, source_type, sources, summary, latency
        )
        
        assert result == str(mock_created_record.id)
        
        summaries.db.create.assert_called_once()
        call_args = summaries.db.create.call_args
        
        data = call_args[0][1]
        assert data['entity_id'] == entity_id
        assert data['source_type'] == source_type.value
        assert data['sources'] == sources
        assert data['summary'] == 'Great hotel with excellent service'
        assert data['positive_tags'] == []
        assert data['negative_tags'] == []
        assert data['content_metadata']['logfire_session_id'] == summaries.SESSION_ID
        assert data['content_metadata']['cost'] == 0.0035
        assert data['content_metadata']['latency'] == 2.5
    
    @pytest.mark.asyncio
    async def test__write_summary_ai__database_error(self, mock_summaries_for_write):
        summaries = mock_summaries_for_write
        
        entity_id = str(uuid.uuid4())
        source_type = Source_Type.CLIENT_SUPPLIER_REVIEWS
        sources = [str(uuid.uuid4())]
        summary = {
            'summary': 'Test summary',
            'positive_tags': ['Good'],
            'negative_tags': ['Bad'],
            'cost': 0.001
        }
        latency = 1.0
        
        summaries.db.create.side_effect = Exception('Database connection failed')
        
        with pytest.raises(Exception, match = 'Database connection failed'):
            await summaries._write_summary_to_ai_schema(
                entity_id, source_type, sources, summary, latency
            )
        
        summaries.db.create.assert_called_once()
