# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["QueueRetrieveParams"]


class QueueRetrieveParams(TypedDict, total=False):
    model: Required[str]
    """Model name"""

    request_id: Required[str]
    """Request ID"""
