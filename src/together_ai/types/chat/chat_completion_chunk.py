# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .usage import Usage
from ..._models import BaseModel

__all__ = ["ChatCompletionChunk", "Token", "Choice", "ChoiceDelta"]


class Token(BaseModel):
    id: int

    logprob: float

    special: bool

    text: str


class ChoiceDelta(BaseModel):
    content: str


class Choice(BaseModel):
    delta: ChoiceDelta

    index: int


class ChatCompletionChunk(BaseModel):
    id: str

    token: Token

    choices: List[Choice]

    created: int

    object: Literal["chat.completion.chunk"]

    finish_reason: Optional[Literal["stop", "eos", "length", "tool_calls"]] = None

    usage: Optional[Usage] = None
