# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .weight_sync_type import WeightSyncType

__all__ = ["OperationWeightsSyncParams"]


class OperationWeightsSyncParams(TypedDict, total=False):
    weight_sync_type: Required[WeightSyncType]
    """How updated parameters are made available for sampling.

    See `WeightSyncType` for accepted values.
    """
