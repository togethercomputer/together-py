# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union

from ...._models import BaseModel

__all__ = ["WeightsSyncResult"]


class WeightsSyncResult(BaseModel):
    """Result of a weights-sync operation"""

    weights_version: Union[str, int]
    """
    Policy version now available for sampling, or queued to become available for
    deferred sync modes. Comparable to `policy_segments[].version` on sample
    results.
    """
