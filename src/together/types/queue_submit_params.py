# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, TypedDict

__all__ = ["QueueSubmitParams"]


class QueueSubmitParams(TypedDict, total=False):
    model: Required[str]
    """Required model identifier"""

    payload: Required[Dict[str, object]]

    info: Dict[str, object]

    priority: int
