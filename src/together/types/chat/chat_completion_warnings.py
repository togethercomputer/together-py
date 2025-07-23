# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from ..._models import BaseModel

__all__ = ["ChatCompletionWarnings", "ChatCompletionWarningItem"]


class ChatCompletionWarningItem(BaseModel):
    message: str


ChatCompletionWarnings: TypeAlias = List[ChatCompletionWarningItem]
