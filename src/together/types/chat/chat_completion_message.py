# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from ..tool_choice import ToolChoice

__all__ = ["ChatCompletionMessage", "FunctionCall"]


class FunctionCall(BaseModel):
    arguments: str

    name: str


class ChatCompletionMessage(BaseModel):
    content: Optional[str] = None

    role: Literal["assistant"]

    function_call: Optional[FunctionCall] = None

    reasoning: Optional[str] = None

    tool_calls: Optional[List[ToolChoice]] = None
