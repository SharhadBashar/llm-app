from pydantic import BaseModel, Field, model_validator
from typing import Dict, Literal, Optional, Tuple, Any, Union
from core.content_enrichment.models import Function, OutputFormat, Tone

class BaseContext(BaseModel):
    tone: Optional[Tone] = None

class GenerateContext(BaseContext):
    user_instructions: str
    existing_text: Optional[str] = None

class RewriteContext(BaseContext):
    existing_text: str
    user_instructions: Optional[str] = None

class ContentEnrichmentRequest(BaseModel):
    metadata: Dict[str, Any] = Field(..., description="Metadata containing block_id")
    output_format: OutputFormat = Field(..., description="Output format for the generated content")
    generate: Optional[GenerateContext] = Field(None, description="Generate function data")
    elaborate: Optional[RewriteContext] = Field(None, description="Elaborate function data")
    polish: Optional[RewriteContext] = Field(None, description="Polish function data")
    shorten: Optional[RewriteContext] = Field(None, description="Shorten function data")
    change_my_tone: Optional[RewriteContext] = Field(None, description="Change tone function data")

    class Config:
        # This allows both enum values and string values
        use_enum_values = False

    @model_validator(mode='after')
    def validate_request(self):
        # First validate that exactly one function is present
        function_values = [f.value for f in Function]
        valid_function_keys = [k for k in self.model_dump() if k != 'metadata' and k != 'output_format']
        function_keys = [k for k in self.model_dump() if k in function_values and getattr(self, k) is not None]
        if len(function_keys) != 1:
            raise ValueError(f"Request must have exactly one function key from {valid_function_keys}")
        
        function_key = function_keys[0]
        context = getattr(self, function_key)

        # Validate function-specific requirements
        if function_key == Function.GENERATE:
            if not context.user_instructions:
                raise ValueError("generate function requires user_instructions")
        else:  # All other functions are rewrite operations
            if not context.existing_text:
                raise ValueError(f"{function_key} function requires existing_text")
            
            # Special validation for change_my_tone
            if function_key == Function.CHANGE_MY_TONE:
                if not context.tone:
                    raise ValueError("change_my_tone function requires tone field")
                # Use the enum values for validation
                valid_tones = [t.value for t in Tone]
                tone_str = context.tone.value if hasattr(context.tone, 'value') else context.tone
                if tone_str not in valid_tones:
                    raise ValueError(f"you passed '{context.tone}' but change_my_tone function requires tone to be one of: {', '.join(valid_tones)}")

        return self

    def get_function_data(self) -> Tuple[str, Union[GenerateContext, RewriteContext]]:
        """
        Returns the function key and its data from the request.
        Only one function key should be present in the request.
        """
        function_values = [f.value for f in Function]
        function_keys = [k for k in self.model_dump() if k in function_values and getattr(self, k) is not None]
        if len(function_keys) != 1:
            raise ValueError("Request must have exactly one function key")
        function_key = function_keys[0]
        # Ensure function_key is lowercase to match database enum
        return function_key.lower(), getattr(self, function_key)

class ParsedContentEnrichmentResponse(BaseModel):
    id: str
    text: str
