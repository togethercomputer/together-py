# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["EvalListParams"]


class EvalListParams(TypedDict, total=False):
    limit: int

    status: str

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """Admin users can specify a user ID to filter jobs.

    Pass empty string to get all jobs.
    """
