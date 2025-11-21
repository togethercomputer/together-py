# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel
from .chat.chat_completion_usage import ChatCompletionUsage

__all__ = ["RerankCreateResponse", "Result", "ResultDocument"]


class ResultDocument(BaseModel):
    text: Optional[str] = None


class Result(BaseModel):
    document: ResultDocument

    index: int

    relevance_score: float


class RerankCreateResponse(BaseModel):
    model: str
    """The model to be used for the rerank request."""

    object: Literal["rerank"]
    """Object type"""

    results: List[Result]

    id: Optional[str] = None
    """Request ID"""

    usage: Optional[ChatCompletionUsage] = None
