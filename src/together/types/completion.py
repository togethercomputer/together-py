# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel
from .log_probs import LogProbs
from .chat.chat_completion_usage import ChatCompletionUsage
from .chat.chat_completion_prompt import ChatCompletionPrompt

__all__ = ["Completion", "Choice"]


class Choice(BaseModel):
    finish_reason: Optional[Literal["stop", "eos", "length", "tool_calls", "function_call"]] = None

    logprobs: Optional[LogProbs] = None

    seed: Optional[int] = None

    text: Optional[str] = None


class Completion(BaseModel):
    id: str

    choices: List[Choice]

    created: int

    model: str

    object: Literal["text.completion"]
    """The object type, which is always `text.completion`."""

    prompt: ChatCompletionPrompt
    """When `echo` is true, the prompt is included in the response.

    Additionally, when `logprobs` is also provided, log probability information is
    provided on the prompt.
    """

    usage: Optional[ChatCompletionUsage] = None
