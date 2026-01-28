# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["QueueCancelParams"]


class QueueCancelParams(TypedDict, total=False):
    model: Required[str]

    request_id: Required[str]
