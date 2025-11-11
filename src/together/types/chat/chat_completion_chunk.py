# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from ..tool_choice import ToolChoice
from .chat_completion_usage import ChatCompletionUsage
from .chat_completion_warning import ChatCompletionWarning

__all__ = ["ChatCompletionChunk", "Choice", "ChoiceDelta", "ChoiceDeltaFunctionCall"]


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
    delta: ChoiceDelta

    finish_reason: Optional[Literal["stop", "eos", "length", "tool_calls", "function_call"]] = None

    index: int

    logprobs: Optional[float] = None

    seed: Optional[int] = None


class ChatCompletionChunk(BaseModel):
    id: str

    choices: List[Choice]

    created: int

    model: str

    object: Literal["chat.completion.chunk"]

    system_fingerprint: Optional[str] = None

    usage: Optional[ChatCompletionUsage] = None

    warnings: Optional[List[ChatCompletionWarning]] = None
