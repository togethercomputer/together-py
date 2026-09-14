# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .adam_config import AdamConfig
from .muon_config import MuonConfig

__all__ = ["OptimizerConfig"]


class OptimizerConfig(BaseModel):
    """Optimizer configuration"""

    adam: Optional[AdamConfig] = None
    """Use the Adam optimizer."""

    muon: Optional[MuonConfig] = None
    """Use the Muon optimizer."""
