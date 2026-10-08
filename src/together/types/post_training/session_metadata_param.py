# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .wandb_metadata_param import WandbMetadataParam

__all__ = ["SessionMetadataParam"]


class SessionMetadataParam(TypedDict, total=False):
    """Auxiliary metadata associated with a training session"""

    wandb: WandbMetadataParam
    """Weights & Biases details associated with the training session"""
