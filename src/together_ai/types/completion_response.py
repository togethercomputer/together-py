# File generated from our OpenAPI spec by Stainless.

from typing import Optional, List

from typing_extensions import Literal

from .chat import Usage

from typing import Optional, Union, List, Dict, Any
from typing_extensions import Literal
from pydantic import Field as FieldInfo
from .._models import BaseModel
from ..types import shared

__all__ = ["CompletionResponse", "Choice", "ChoiceLogprobs", "Prompt", "PromptLogprobs"]

class ChoiceLogprobs(BaseModel):
    token_logprobs: Optional[List[float]] = None
    """List of token log probabilities"""

    tokens: Optional[List[str]] = None
    """List of token strings"""

class Choice(BaseModel):
    finish_reason: Optional[Literal["stop", "eos", "length", "tool_calls"]] = None

    logprobs: Optional[ChoiceLogprobs] = None

    text: Optional[str] = None

class PromptLogprobs(BaseModel):
    token_logprobs: Optional[List[float]] = None
    """List of token log probabilities"""

    tokens: Optional[List[str]] = None
    """List of token strings"""

class Prompt(BaseModel):
    logprobs: Optional[PromptLogprobs] = None

    text: Optional[str] = None

class CompletionResponse(BaseModel):
    id: str

    choices: List[Choice]

    created: int

    model: str

    object: Literal["text_completion"]

    usage: Usage

    prompt: Optional[List[Prompt]] = None