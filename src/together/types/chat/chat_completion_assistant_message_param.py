# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

from ..tool_choice_param import ToolChoiceParam

__all__ = ["ChatCompletionAssistantMessageParam"]


class ChatCompletionAssistantMessageParam(TypedDict, total=False):
    role: Required[Literal["assistant"]]

    content: Optional[str]

    name: str

    reasoning: Optional[str]

    reasoning_content: Optional[str]

    tool_calls: Iterable[ToolChoiceParam]
