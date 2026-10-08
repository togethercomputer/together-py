# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["CheckpointListParams"]


class CheckpointListParams(TypedDict, total=False):
    after: str
    """Cursor for pagination (ID of the last checkpoint from the previous page)"""

    base_model: str
    """Only return checkpoints trained from this base model. Match is exact."""

    limit: int
    """Maximum number of checkpoints to return (1-100)"""

    session_id: str
    """Only return checkpoints produced by this training session"""

    type: Literal["CHECKPOINT_TYPE_TRAINING", "CHECKPOINT_TYPE_INFERENCE"]
    """Only return checkpoints of this type.

    CHECKPOINT_TYPE_TRAINING is the full training state (weights and optimizer
    state), for resuming a training session with its optimizer state;
    CHECKPOINT_TYPE_INFERENCE is a model ready for serving or download, also added
    to your models. When set, it must be CHECKPOINT_TYPE_TRAINING or
    CHECKPOINT_TYPE_INFERENCE; when omitted, checkpoints of both types are returned.
    """
