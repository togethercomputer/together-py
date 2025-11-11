# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel
from .tool_choice import ToolChoice
from .chat.chat_completion_usage import ChatCompletionUsage

__all__ = ["CompletionChunk", "Token", "Choice", "ChoiceDelta", "ChoiceDeltaFunctionCall"]


class Token(BaseModel):
    id: int

    logprob: float

    special: bool

    text: str


class ChoiceDeltaFunctionCall(BaseModel):
    arguments: str

    name: str


class ChoiceDelta(BaseModel):
    role: Literal["system", "user", "assistant", "function", "tool"]

    content: Optional[str] = None

    function_call: Optional[ChoiceDeltaFunctionCall] = None

    reasoning: Optional[str] = None

    token_id: Optional[int] = None

    tool_calls: Optional[List[ToolChoice]] = None


class Choice(BaseModel):
    index: int

    delta: Optional[ChoiceDelta] = None

    text: Optional[str] = None


class CompletionChunk(BaseModel):
    id: str

    token: Token

    choices: List[Choice]

    finish_reason: Optional[Literal["stop", "eos", "length", "tool_calls", "function_call"]] = None

    usage: Optional[ChatCompletionUsage] = None

    created: Optional[int] = None

    object: Optional[Literal["completion.chunk"]] = None

    seed: Optional[int] = None
