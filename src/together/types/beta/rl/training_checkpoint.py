# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from datetime import datetime

from ...._models import BaseModel
from .model_registry_artifact import ModelRegistryArtifact

__all__ = ["TrainingCheckpoint"]


class TrainingCheckpoint(BaseModel):
    """Saved training checkpoint"""

    id: str
    """Unique identifier for the checkpoint"""

    created_at: datetime
    """Timestamp when the checkpoint was created"""

    step: Union[str, int]
    """Training step at time of save"""

    registration: Optional[ModelRegistryArtifact] = None
    """
    Model registry artifact holding this checkpoint's training state, used to resume
    training rather than to deploy. Absent when the checkpoint was not uploaded to
    the registry.
    """
