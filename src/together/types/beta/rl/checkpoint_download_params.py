# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ...post_training.checkpoint_variant import CheckpointVariant

__all__ = ["CheckpointDownloadParams"]


class CheckpointDownloadParams(TypedDict, total=False):
    variant: Required[CheckpointVariant]
    """Files to download.

    CHECKPOINT_VARIANT_MERGED is the full model with the trained weights applied;
    CHECKPOINT_VARIANT_ADAPTER is the LoRA adapter weights only, available for
    checkpoints from LoRA training sessions.
    """
