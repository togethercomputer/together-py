# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .adam_params import AdamParams
from .muon_params import MuonParams
from .weight_sync_type import WeightSyncType

__all__ = ["OperationOptimStepParams"]


class OperationOptimStepParams(TypedDict, total=False):
    weight_sync_type: Required[WeightSyncType]
    """
    How the trainer's updated weights are propagated to the generator after this
    optimizer step. See `WeightSyncType` for accepted values.
    """

    adam_params: AdamParams
    """Adam optimizer overrides for this step."""

    muon_params: MuonParams
    """Muon optimizer overrides for this step."""
