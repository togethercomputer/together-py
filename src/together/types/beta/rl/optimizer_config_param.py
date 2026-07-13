# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .muon_optimizer_config_param import MuonOptimizerConfigParam
from .adamw_optimizer_config_param import AdamwOptimizerConfigParam

__all__ = ["OptimizerConfigParam"]


class OptimizerConfigParam(TypedDict, total=False):
    """Optimizer configuration"""

    adamw: AdamwOptimizerConfigParam
    """Use the AdamW optimizer."""

    muon: MuonOptimizerConfigParam
    """Use the Muon optimizer."""
