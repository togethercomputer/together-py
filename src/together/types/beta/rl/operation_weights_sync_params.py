# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .weight_sync_type import WeightSyncType

__all__ = ["OperationWeightsSyncParams"]


class OperationWeightsSyncParams(TypedDict, total=False):
    weight_sync_type: Required[WeightSyncType]
    """How updated parameters are made available for sampling.

    See `WeightSyncType` for accepted values.
    """

    idempotency_key: Required[Annotated[str, PropertyInfo(alias="Idempotency-Key")]]
    """
    Required key that makes retries return the original operation; use a new key for
    changed request bodies.
    """
