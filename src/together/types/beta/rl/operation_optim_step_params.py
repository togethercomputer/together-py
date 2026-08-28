# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .adam_params import AdamParams
from .muon_params import MuonParams

__all__ = ["OperationOptimStepParams"]


class OperationOptimStepParams(TypedDict, total=False):
    adam_params: AdamParams
    """Adam optimizer overrides for this step."""

    muon_params: MuonParams
    """Muon optimizer overrides for this step."""
