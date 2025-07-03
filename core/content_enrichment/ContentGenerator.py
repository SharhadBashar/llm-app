from llms.factory import LLMFetcher
from .prompts import (
    BASE_INSTRUCTIONS_MAP, MARKDOWN_INSTRUCTIONS, 
    make_rewrite_prompt, make_generate_prompt
    )
from utils.usage_tracker import UsageTracker, TokenUsage
from .serializers import ContentEnrichmentRequest
from .models import Function, OutputFormat

class ContentGenerator:
    def __init__(self, request: ContentEnrichmentRequest):
        self.function_key, self.context = request.get_function_data()
        self.output_format = request.output_format
        self.LLMFetcher = LLMFetcher(
            model='gpt-4.1-mini',
            provider='openai'
        )
        self.usage_tracker = UsageTracker()

    async def generate(self):
        instructions = self._compile_instructions()
        input_prompt = self._compile_prompt()
        response, model, cost = await self._call_llm(instructions, input_prompt)
        return response, model, cost

    def _compile_instructions(self):
        base_instructions = []
        if (self.function_key == Function.GENERATE and self.context.existing_text) or self.function_key == Function.CHANGE_MY_TONE:
            base_instructions.append(self._get_base_instructions('REWRITE'))
        else:
            base_instructions.append(self._get_base_instructions())

        if self.function_key == Function.CHANGE_MY_TONE:
            change_my_tone_instructions = self._get_base_instructions(Function.CHANGE_MY_TONE)
            if change_my_tone_instructions:
                base_instructions.append(change_my_tone_instructions.get(self.context.tone))
            
        if self.output_format == OutputFormat.HTML:
            base_instructions.append(MARKDOWN_INSTRUCTIONS)
        return '\n\n'.join(base_instructions)

    def _compile_prompt(self):
        if self.function_key == Function.GENERATE:
            if self.context.existing_text:
                # Help me write with existing text
                return make_rewrite_prompt(self.context.existing_text, self.context.user_instructions)
            # Help me write from scratch
            return make_generate_prompt(self.context.user_instructions)
        # every other function
        return make_rewrite_prompt(self.context.existing_text)

    def _get_base_instructions(self, explicit_function_key: str = None):
        if explicit_function_key:
            return BASE_INSTRUCTIONS_MAP.get(explicit_function_key)
        return BASE_INSTRUCTIONS_MAP.get(self.function_key)
    
    def _calculate_cost(self, usage, model) -> float:
        '''
        This method is reliant on external services (ex. Open AI) keeping model/model snapshot names, and the usage object structure the same.
        It's wrapped in a try except because, even if this calculation fails, we would want the request to succeed.
        This calculation is performed for storing the data and cost analysis.
        '''
        try:
            # Convert the llm's usage class to a dict of our relevant items then unpack
            usage_dict = {
                'input_tokens': usage.input_tokens,
                'output_tokens': usage.output_tokens,
                'total_tokens': usage.total_tokens,
                'input_tokens_details': usage.input_tokens_details,
                'output_tokens_details': usage.output_tokens_details,
                'model': model
            }
            token_usage = TokenUsage(**usage_dict)
            cost = self.usage_tracker.track_usage(token_usage)
            return cost
        except Exception as e:
            raise ValueError(f"Couldn't parse usage correctly: {e}")

    def _replace_newline_with_br(self, text: str) -> str:
        """Replace all newline characters with <br> tags"""
        return text.replace('\n', '<br>')

    async def _call_llm(self, instructions, prompt):
        response = await self.LLMFetcher.async_client.responses.create(
            model=self.LLMFetcher.model,
            instructions=instructions,
            input=prompt
        )

        response_text = response.output_text

        try:
            cost = self._calculate_cost(response.usage, response.model)
        except ValueError as e:
            print(f"Cost calculation failed for model {response.model}: {str(e)} (usage: {response.usage})")
            cost = None
            
        return response_text, response.model, cost
    
