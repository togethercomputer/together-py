# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .muon_optimizer_config import MuonOptimizerConfig

__all__ = ["OptimizerConfig"]


class OptimizerConfig(BaseModel):
    """Optimizer configuration"""

    adamw: Optional[object] = None
    """Use the AdamW optimizer."""

    muon: Optional[MuonOptimizerConfig] = None
    """Use the Muon optimizer."""
