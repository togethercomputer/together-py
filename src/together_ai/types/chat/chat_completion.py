# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .usage import Usage
from ..._models import BaseModel

__all__ = ["ChatCompletion", "Choice", "ChoiceLogprobs", "ChoiceMessage"]


class ChoiceLogprobs(BaseModel):
    token_logprobs: Optional[List[float]] = None
    """List of token log probabilities"""

    tokens: Optional[List[str]] = None
    """List of token strings"""


class ChoiceMessage(BaseModel):
    content: str

    role: str


class Choice(BaseModel):
    finish_reason: Optional[Literal["stop", "eos", "length", "tool_calls"]] = None

    logprobs: Optional[ChoiceLogprobs] = None

    message: Optional[ChoiceMessage] = None


class ChatCompletion(BaseModel):
    id: str

    choices: List[Choice]

    created: Optional[int] = None

    model: Optional[str] = None

    object: Optional[Literal["chat.completion"]] = None

    usage: Optional[Usage] = None
