# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel
from .chat.usage import Usage

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

    usage: Optional[Usage] = None

    prompt: Optional[List[Prompt]] = None
