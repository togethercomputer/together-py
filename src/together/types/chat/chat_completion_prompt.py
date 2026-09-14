# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import TypeAlias

from ..._models import BaseModel
from ..log_probs import LogProbs

__all__ = ["ChatCompletionPrompt", "ChatCompletionPromptItem"]


class ChatCompletionPromptItem(BaseModel):
    logprobs: Optional[LogProbs] = None

    text: Optional[str] = None


ChatCompletionPrompt: TypeAlias = List[ChatCompletionPromptItem]
