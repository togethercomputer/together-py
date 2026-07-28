# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .weight_sync_type import WeightSyncType
from .muon_optimizer_params import MuonOptimizerParams
from .adamw_optimizer_params import AdamwOptimizerParams

__all__ = ["OperationOptimStepParams"]


class OperationOptimStepParams(TypedDict, total=False):
    weight_sync_type: Required[WeightSyncType]
    """
    How the trainer's updated weights are propagated to the generator after this
    optimizer step. See `WeightSyncType` for accepted values.
    """

    adamw_params: AdamwOptimizerParams
    """Per-step AdamW optimizer overrides."""

    max_grad_norm: float
    """
    Maximum gradient norm for this step, gradients across all model parameters are
    clipped to this value. Set to 0 to disable gradient clipping. When unset,
    gradients are clipped to the session default (1.0).
    """

    muon_params: MuonOptimizerParams
    """Per-step Muon optimizer overrides"""
