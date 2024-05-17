# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel
from .log_probs import LogProbs
from .chat.usage import Usage

__all__ = ["CompletionResponse", "Choice", "Prompt"]


class Choice(BaseModel):
    finish_reason: Optional[Literal["stop", "eos", "length", "tool_calls"]] = None

    logprobs: Optional[LogProbs] = None

    text: Optional[str] = None


class Prompt(BaseModel):
    logprobs: Optional[LogProbs] = None

    text: Optional[str] = None


class CompletionResponse(BaseModel):
    id: str

    choices: List[Choice]

    created: int

    model: str

    object: Literal["text_completion"]

    usage: Optional[Usage] = None

    prompt: Optional[List[Prompt]] = None
