# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from ..tool_choice import ToolChoice

__all__ = ["ChatCompletionMessage"]


class ChatCompletionMessage(BaseModel):
    content: Optional[str] = None

    role: Literal["assistant"]

    reasoning: Optional[str] = None

    reasoning_content: Optional[str] = None

    tool_calls: Optional[List[ToolChoice]] = None
