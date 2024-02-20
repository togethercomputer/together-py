# File generated from our OpenAPI spec by Stainless.

from typing import Optional, List

from typing_extensions import Literal

from typing import Optional, Union, List, Dict, Any
from typing_extensions import Literal
from pydantic import Field as FieldInfo
from ..._models import BaseModel
from ...types import shared

__all__ = ["ChatCompletionResponse", "Choice", "ChoiceLogprobs", "ChoiceMessage", "Usage"]

class ChoiceLogprobs(BaseModel):
    token_logprobs: Optional[List[float]] = None
    """List of token log probabilities"""

    tokens: Optional[List[str]] = None
    """List of token strings"""

class ChoiceMessage(BaseModel):
    content: Optional[str] = None

    role: Optional[str] = None

class Choice(BaseModel):
    finish_reason: Optional[Literal["stop", "eos", "length", "tool_calls"]] = None

    logprobs: Optional[ChoiceLogprobs] = None

    message: Optional[ChoiceMessage] = None

class Usage(BaseModel):
    completion_tokens: Optional[int] = None

    prompt_tokens: Optional[int] = None

    total_tokens: Optional[int] = None

class ChatCompletionResponse(BaseModel):
    id: Optional[str] = None

    choices: Optional[List[Choice]] = None

    created: Optional[int] = None

    model: Optional[str] = None

    object: Optional[Literal["chat.completion"]] = None

    usage: Optional[Usage] = None