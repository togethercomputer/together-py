# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from datetime import datetime

from ...._models import BaseModel

__all__ = ["TrainingCheckpoint", "Registration"]


class Registration(BaseModel):
    """
    Together model registry details, set when the checkpoint was uploaded to the registry
    """

    object_id: str
    """Together model registry object ID for the training checkpoint artifact (e.g.

    `ml_...`)
    """

    object_revision_id: Optional[str] = None
    """Together model registry revision ID for the training checkpoint artifact (e.g.

    `rv_...`), empty when the upload reported no revision
    """


class TrainingCheckpoint(BaseModel):
    """Saved training checkpoint"""

    id: str
    """Unique identifier for the checkpoint"""

    created_at: datetime
    """Timestamp when the checkpoint was created"""

    step: Union[str, int]
    """Training step at time of save"""

    registration: Optional[Registration] = None
    """
    Together model registry details, set when the checkpoint was uploaded to the
    registry
    """
