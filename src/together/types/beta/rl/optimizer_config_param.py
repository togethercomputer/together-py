# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .adam_config_param import AdamConfigParam
from .muon_config_param import MuonConfigParam

__all__ = ["OptimizerConfigParam"]


class OptimizerConfigParam(TypedDict, total=False):
    """Optimizer configuration"""

    adam: AdamConfigParam
    """Use the Adam optimizer."""

    muon: MuonConfigParam
    """Use the Muon optimizer."""
