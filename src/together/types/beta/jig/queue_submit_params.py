# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, TypedDict

__all__ = ["QueueSubmitParams"]


class QueueSubmitParams(TypedDict, total=False):
    model: Required[str]
    """Required model identifier"""

    payload: Required[Dict[str, object]]
    """Freeform model input.

    Passed unchanged to the model. Contents are model-specific.
    """

    info: Dict[str, object]
    """Arbitrary JSON metadata stored with the job and returned in status responses.

    The model and system may add or update keys during processing.
    """

    priority: int
    """Job priority.

    Higher values are processed first (strict priority ordering). Jobs with equal
    priority are processed in submission order (FIFO).
    """
