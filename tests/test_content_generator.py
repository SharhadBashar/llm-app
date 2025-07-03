import pytest
from decimal import Decimal

from core.content_enrichment.ContentGenerator import ContentGenerator
from core.content_enrichment.models import Function, Tone
from core.content_enrichment.prompts import (
    GENERATE_INSTRUCTIONS, REWRITE_INSTRUCTIONS, ELABORATE_INSTRUCTIONS,
    MARKDOWN_INSTRUCTIONS, CHANGE_MY_TONE_INSTRUCTIONS_MAP
)

class TestContentGenerator:
    """Test suite for ContentGenerator class"""

    @pytest.mark.asyncio
    async def test_generate_html(self, generate_request_html, mock_llm_fetcher):
        """Test generate from scratch with HTML output"""
        generator = ContentGenerator(generate_request_html)
        response_text, model, cost = await generator.generate()
        
        # Verify instructions
        expected_instructions = f"{GENERATE_INSTRUCTIONS}\n\n{MARKDOWN_INSTRUCTIONS}"
        mock_llm_fetcher.async_client.responses.create.assert_called_once()
        call_args = mock_llm_fetcher.async_client.responses.create.call_args[1]
        assert call_args['instructions'] == expected_instructions
        
        # Verify response
        assert response_text == "Test generated content"
        assert model == "gpt-4.1-mini"
        assert cost == Decimal('0.4016')

    @pytest.mark.asyncio
    async def test_generate_text(self, generate_request_text, mock_llm_fetcher):
        """Test generate from scratch with text output"""
        generator = ContentGenerator(generate_request_text)
        response_text, model, cost = await generator.generate()
        
        # Verify instructions
        mock_llm_fetcher.async_client.responses.create.assert_called_once()
        call_args = mock_llm_fetcher.async_client.responses.create.call_args[1]
        assert call_args['instructions'] == GENERATE_INSTRUCTIONS
        
        # Verify response
        assert response_text == "Test generated content"
        assert model == "gpt-4.1-mini"
        assert cost == Decimal('0.4016')

    @pytest.mark.asyncio
    async def test_generate_with_existing_html(self, generate_with_existing_html, mock_llm_fetcher):
        """Test generate with existing text and HTML output"""
        generator = ContentGenerator(generate_with_existing_html)
        response_text, model, cost = await generator.generate()
        
        # Verify instructions
        expected_instructions = f"{REWRITE_INSTRUCTIONS}\n\n{MARKDOWN_INSTRUCTIONS}"
        mock_llm_fetcher.async_client.responses.create.assert_called_once()
        call_args = mock_llm_fetcher.async_client.responses.create.call_args[1]
        assert call_args['instructions'] == expected_instructions
        
        # Verify response
        assert response_text == "Test generated content"
        assert model == "gpt-4.1-mini"
        assert cost == Decimal('0.4016')

    @pytest.mark.asyncio
    async def test_elaborate_html(self, elaborate_request_html, mock_llm_fetcher):
        """Test elaborate with HTML output"""
        generator = ContentGenerator(elaborate_request_html)
        response_text, model, cost = await generator.generate()
        
        # Verify instructions
        expected_instructions = f"{ELABORATE_INSTRUCTIONS}\n\n{MARKDOWN_INSTRUCTIONS}"
        mock_llm_fetcher.async_client.responses.create.assert_called_once()
        call_args = mock_llm_fetcher.async_client.responses.create.call_args[1]
        assert call_args['instructions'] == expected_instructions
        
        # Verify response
        assert response_text == "Test generated content"
        assert model == "gpt-4.1-mini"
        assert cost == Decimal('0.4016')

    @pytest.mark.asyncio
    async def test_change_tone_html(self, change_tone_request_html, mock_llm_fetcher):
        """Test change tone with HTML output"""
        generator = ContentGenerator(change_tone_request_html)
        response_text, model, cost = await generator.generate()
        
        # Verify instructions
        # Note: The tone is still accessed with lowercase key in the map
        expected_instructions = f"{REWRITE_INSTRUCTIONS}\n\n{CHANGE_MY_TONE_INSTRUCTIONS_MAP.get(Tone.SOPHISTICATED)}\n\n{MARKDOWN_INSTRUCTIONS}"
        mock_llm_fetcher.async_client.responses.create.assert_called_once()
        call_args = mock_llm_fetcher.async_client.responses.create.call_args[1]
        assert call_args['instructions'] == expected_instructions
        
        # Verify response
        assert response_text == "Test generated content"
        assert model == "gpt-4.1-mini"
        assert cost == Decimal('0.4016')
