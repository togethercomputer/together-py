# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["BatchCreateParams"]


class BatchCreateParams(TypedDict, total=False):
    endpoint: Required[str]
    """The endpoint to use for batch processing"""

    input_file_id: Required[str]
    """ID of the uploaded input file containing batch requests"""

    completion_window: str
    """Time window for batch completion (optional)"""

    model_id: str
    """Model to use for processing batch requests"""

    priority: int
    """Priority for batch processing (optional)"""
