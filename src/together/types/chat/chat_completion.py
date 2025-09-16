# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from ..log_probs import LogProbs
from ..tool_choice import ToolChoice
from .chat_completion_usage import ChatCompletionUsage
from .chat_completion_warning import ChatCompletionWarning

__all__ = ["ChatCompletion", "Choice", "ChoiceMessage", "ChoiceMessageFunctionCall"]


class ChoiceMessageFunctionCall(BaseModel):
    arguments: str

    name: str


class ChoiceMessage(BaseModel):
    content: Optional[str] = None

    role: Literal["assistant"]

    function_call: Optional[ChoiceMessageFunctionCall] = None

    reasoning: Optional[str] = None

    tool_calls: Optional[List[ToolChoice]] = None


class Choice(BaseModel):
    finish_reason: Optional[Literal["stop", "eos", "length", "tool_calls", "function_call"]] = None

    index: Optional[int] = None

    logprobs: Optional[LogProbs] = None

    message: Optional[ChoiceMessage] = None

    seed: Optional[int] = None

    text: Optional[str] = None


class ChatCompletion(BaseModel):
    id: str

    choices: List[Choice]

    created: int

    model: str

    object: Literal["chat.completion"]

    usage: Optional[ChatCompletionUsage] = None

    warnings: Optional[List[ChatCompletionWarning]] = None
