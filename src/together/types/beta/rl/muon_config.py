# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .muon_scaling_strategy import MuonScalingStrategy

__all__ = ["MuonConfig"]


class MuonConfig(BaseModel):
    """Advanced configuration for the Muon optimizer."""

    scaling_strategy: Optional[MuonScalingStrategy] = None
    """Scaling strategy for the Muon optimizer."""
