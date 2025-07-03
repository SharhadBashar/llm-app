'''
    Usage tracking and cost calculation for different AI models.
'''

from dataclasses import dataclass
import sys
from typing import Dict, Optional
from decimal import Decimal

import logfire

# Per 1 million tokens
MODEL_PRICING = {
    # GPT-4.1 Series
    'gpt-4.1': {
        'input': 2.00,
        'cached_input': 0.50,
        'output': 8.00
    },
    'gpt-4.1-mini': {
        'input': 0.40,
        'cached_input': 0.10,
        'output': 1.60
    },
    'gpt-4.1-nano': {
        'input': 0.10,
        'cached_input': 0.025,
        'output': 0.40
    },
    
    # GPT-4.5 Series
    'gpt-4.5-preview': {
        'input': 75.00,
        'cached_input': 37.50,
        'output': 150.00
    },
    
    # GPT-4o Series
    'gpt-4o': {
        'input': 2.50,
        'cached_input': 1.25,
        'output': 10.00
    },
    'gpt-4o-mini': {
        'input': 0.15,
        'cached_input': 0.075,
        'output': 0.60
    },
    'gpt-4o-audio-preview': {
        'input': 2.50,
        'cached_input': None,  # No cached pricing
        'output': 10.00
    },
    'gpt-4o-realtime-preview': {
        'input': 5.00,
        'cached_input': 2.50,
        'output': 20.00
    },
    'gpt-4o-mini-audio-preview': {
        'input': 0.15,
        'cached_input': None,  # No cached pricing
        'output': 0.60
    },
    'gpt-4o-mini-realtime-preview': {
        'input': 0.60,
        'cached_input': 0.30,
        'output': 2.40
    },
    'gpt-4o-mini-search-preview': {
        'input': 0.15,
        'cached_input': None,  # No cached pricing
        'output': 0.60
    },
    'gpt-4o-search-preview': {
        'input': 2.50,
        'cached_input': None,  # No cached pricing
        'output': 10.00
    },
    
    # O Series
    'o1': {
        'input': 15.00,
        'cached_input': 7.50,
        'output': 60.00
    },
    'o1-pro': {
        'input': 150.00,
        'cached_input': None,  # No cached pricing
        'output': 600.00
    },
    'o1-mini': {
        'input': 1.10,
        'cached_input': 0.55,
        'output': 4.40
    },
    'o3': {
        'input': 10.00,
        'cached_input': 2.50,
        'output': 40.00
    },
    'o3-mini': {
        'input': 1.10,
        'cached_input': 0.55,
        'output': 4.40
    },
    'o4-mini': {
        'input': 1.10,
        'cached_input': 0.275,
        'output': 4.40
    },
    
    # Other Models
    'computer-use-preview': {
        'input': 3.00,
        'cached_input': None,  # No cached pricing
        'output': 12.00
    }
}

# Add date-suffixed versions of models
def _add_dated_models():
    '''Add date-suffixed versions of models with the same pricing.'''
    dated_models = {
        'gpt-4.1': 'gpt-4.1-2025-04-14',
        'gpt-4.1-mini': 'gpt-4.1-mini-2025-04-14',
        'gpt-4.1-nano': 'gpt-4.1-nano-2025-04-14',
        'gpt-4.5-preview': 'gpt-4.5-preview-2025-02-27',
        'gpt-4o': 'gpt-4o-2024-08-06',
        'gpt-4o-mini': 'gpt-4o-mini-2024-07-18',
        'gpt-4o-audio-preview': 'gpt-4o-audio-preview-2024-12-17',
        'gpt-4o-realtime-preview': 'gpt-4o-realtime-preview-2024-12-17',
        'gpt-4o-mini-audio-preview': 'gpt-4o-mini-audio-preview-2024-12-17',
        'gpt-4o-mini-realtime-preview': 'gpt-4o-mini-realtime-preview-2024-12-17',
        'o1': 'o1-2024-12-17',
        'o1-pro': 'o1-pro-2025-03-19',
        'o3': 'o3-2025-04-16',
        'o4-mini': 'o4-mini-2025-04-16',
        'o3-mini': 'o3-mini-2025-01-31',
        'o1-mini': 'o1-mini-2024-09-12',
        'gpt-4o-mini-search-preview': 'gpt-4o-mini-search-preview-2025-03-11',
        'gpt-4o-search-preview': 'gpt-4o-search-preview-2025-03-11',
        'computer-use-preview': 'computer-use-preview-2025-03-11'
    }
    
    for base_model, dated_model in dated_models.items():
        if base_model in MODEL_PRICING:
            MODEL_PRICING[dated_model] = MODEL_PRICING[base_model]

_add_dated_models()

@dataclass
class InputTokensDetails:
    '''Details about input token usage.'''
    cached_tokens: int = 0

@dataclass
class OutputTokensDetails:
    '''Details about output token usage.'''
    reasoning_tokens: int = 0

@dataclass
class TokenUsage:
    '''Represents token usage for a single request, matching OpenAI's response format.'''
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str
    input_tokens_details: Optional[InputTokensDetails] = None
    output_tokens_details: Optional[OutputTokensDetails] = None

    @property
    def is_cached(self) -> bool:
        '''Whether any of the input tokens were cached.'''
        if not self.input_tokens_details:
            return False
        return self.input_tokens_details.cached_tokens > 0

    @property
    def non_cached_input_tokens(self) -> int:
        '''Number of input tokens that were not cached.'''
        if not self.input_tokens_details:
            return self.input_tokens
        return self.input_tokens - self.input_tokens_details.cached_tokens

class UsageTracker:
    '''
        Tracks and calculates costs for AI model usage.
        This tracker maintains cumulative totals of tokens and costs for each model.
        Use reset() to clear the tracking data when needed.
    '''
    
    def __init__(self):
        self.total_costs: Dict[str, Decimal] = {}  # Model -> total cost
        self.total_tokens: Dict[str, Dict[str, int]] = {}  # Model -> {input/output/cached} -> count
    
    def _calculate_cost(self, model: str, usage: TokenUsage) -> Decimal:
        '''Calculate the cost for a given model and token usage.'''
        if model not in MODEL_PRICING:
            raise ValueError(f'Unknown model: {model}')
        
        pricing = MODEL_PRICING[model]
        
        # Calculate costs for cached and non-cached input tokens separately
        cached_input_cost = Decimal('0')
        if usage.input_tokens_details and usage.input_tokens_details.cached_tokens and pricing['cached_input'] is not None:
            cached_input_cost = (
                Decimal(str(usage.input_tokens_details.cached_tokens)) / 
                Decimal('1000000') * 
                Decimal(str(pricing['cached_input']))
            )
        
        non_cached_input_cost = (
            Decimal(str(usage.non_cached_input_tokens)) / 
            Decimal('1000000') * 
            Decimal(str(pricing['input']))
        )
        
        output_cost = (
            Decimal(str(usage.output_tokens)) / 
            Decimal('1000000') * 
            Decimal(str(pricing['output']))
        )
        
        return cached_input_cost + non_cached_input_cost + output_cost
    
    def track_usage(self, usage: TokenUsage) -> Decimal:
        '''
            Track usage and return the cost for this request.
            This method adds to the cumulative totals for the model.
            The totals persist until reset() is called.
        '''
        cost = self._calculate_cost(usage.model, usage)
        
        # Update totals
        if usage.model not in self.total_costs:
            self.total_costs[usage.model] = Decimal('0')
            self.total_tokens[usage.model] = {
                'input': 0,
                'output': 0,
                'cached_input': 0
            }
        
        self.total_costs[usage.model] += cost
        self.total_tokens[usage.model]['input'] += usage.input_tokens
        self.total_tokens[usage.model]['output'] += usage.output_tokens
        if usage.input_tokens_details:
            self.total_tokens[usage.model]['cached_input'] += usage.input_tokens_details.cached_tokens
        
        return cost
    
    def get_total_cost(self, model: Optional[str] = None) -> Decimal:
        '''Get total cost for a specific model or all models.'''
        if model:
            return self.total_costs.get(model, Decimal('0'))
        return sum(self.total_costs.values())
    
    def get_responses_cost_simple(self, model: str, usage) -> float:
        try:
            return (
                MODEL_PRICING[model]['input'] * usage.input_tokens / 1_000_000 +
                MODEL_PRICING[model]['output'] * usage.output_tokens / 1_000_000 +
                MODEL_PRICING[model]['cached_input'] * usage.input_tokens_details.cached_tokens / 1_000_000
            )
        except Exception as e:
            logfire.error(f'Error in {self.__class__.__name__}.{self.get_responses_cost_simple.__name__}: {e}')
            return 0

    def get_total_tokens(self, model: Optional[str] = None) -> Dict[str, Dict[str, int]]:
        '''Get total tokens for a specific model or all models.'''
        if model:
            return {model: self.total_tokens.get(model, {'input': 0, 'output': 0, 'cached_input': 0})}
        return self.total_tokens
    
    def reset(self, model: Optional[str] = None):
        '''Reset tracking for a specific model or all models.'''
        if model:
            self.total_costs.pop(model, None)
            self.total_tokens.pop(model, None)
        else:
            self.total_costs.clear()
            self.total_tokens.clear()
