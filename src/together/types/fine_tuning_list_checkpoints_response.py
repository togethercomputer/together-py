# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["FineTuningListCheckpointsResponse", "Data"]


class Data(BaseModel):
    """A checkpoint available for a fine-tuning job."""

    checkpoint_type: str
    """
    Display label for the checkpoint, including the final or intermediate checkpoint
    step.
    """

    created_at: str
    """Timestamp when the checkpoint was created."""

    path: str
    """Storage path for the checkpoint artifact."""

    step: int
    """
    Step represented by the checkpoint; final checkpoints use the shipped model
    step.
    """

    checkpoint: Optional[Literal["model", "adapter"]] = None
    """Canonical artifact selector for checkpoint download requests."""

    object_id: Optional[str] = None
    """Together model registry object ID for the checkpoint artifact (e.g. `ml_...`)."""

    object_name: Optional[str] = None
    """
    Together model registry name for the checkpoint artifact, formatted as
    `<project_slug>/<checkpoint_name>`.
    """

    object_revision_id: Optional[str] = None
    """Together model registry revision ID for the checkpoint artifact (e.g.

    `rv_...`).
    """


class FineTuningListCheckpointsResponse(BaseModel):
    data: List[Data]
