import uuid
import pytest
import logfire
from unittest.mock import AsyncMock, patch

from core.summaries.summaries import Summaries
from core.summaries.helper import extract_source_data
from core.summaries.types import Source, Source_Type, Tags, All_Tags

class Test_Summaries_Generation:
    @pytest.fixture
    def mock_summaries_data(self):
        logfire.configure(send_to_logfire = False)
        with patch('core.summaries.summaries.LLMFetcher') as mock_llm_fetcher, \
             patch('core.summaries.summaries.logfire'):  # Patch logfire to prevent actual logging
            
            mock_client = AsyncMock()
            mock_llm_fetcher.return_value.async_client = mock_client
            
            summaries = Summaries()
            summaries.llm = mock_client

            summaries.entity_id = uuid.uuid4()
            summaries.entity_name = 'Test Hotel'
            summaries.source_type = Source_Type.CLIENT_SUPPLIER_REVIEWS
            sources = [
                Source(id = uuid.uuid4(), review='Great hotel'),
                Source(id = uuid.uuid4(), review='Nice service'),
                Source(id = uuid.uuid4(), review='Good value')
            ]
            summaries.source_ids, summaries.source_reviews = extract_source_data(sources)
            return summaries
        
    @pytest.mark.asyncio
    async def test__generate_summary__success(self, mock_summaries_data):
        summaries = mock_summaries_data

        summaries._response = AsyncMock(side_effect = [
            ('Initial summary', 0.001),  # Step 1 return value
            ('Refined summary', 0.002)   # Step 2 return value
        ])
        summaries._response_structured_output = AsyncMock(side_effect = [
            (Tags(tags=['Location', 'Service']), 0.001),  # Positive tags
            (Tags(tags=['Noise', 'Price']), 0.001),       # Negative tags
            (All_Tags(positive_tags=['Location', 'Service'], negative_tags=['Noise']), 0.001)  # Combined tags
        ])

        result, latency = await summaries._generate_summary()
        assert result['summary'] == 'Refined summary'
        assert result['positive_tags'] == ['Location', 'Service']
        assert result['negative_tags'] == ['Noise']
        assert result['cost'] == 0.006
        assert latency > 0    
        assert summaries._response.call_count == 2
        assert summaries._response_structured_output.call_count == 3
