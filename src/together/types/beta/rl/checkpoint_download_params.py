# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .checkpoint_variant import CheckpointVariant

__all__ = ["CheckpointDownloadParams"]


class CheckpointDownloadParams(TypedDict, total=False):
    variant: Required[CheckpointVariant]
    """
    Checkpoint variant to download: merged (full model) or adapter (LoRA weights
    only)
    """
