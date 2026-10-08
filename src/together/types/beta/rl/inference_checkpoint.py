# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from datetime import datetime

from ...._models import BaseModel
from .model_registry_artifact import ModelRegistryArtifact

__all__ = ["InferenceCheckpoint", "Registration"]


class Registration(BaseModel):
    """Model registry artifacts to deploy or download this checkpoint from.

    Absent when the checkpoint was not uploaded to the registry.
    """

    adapter: Optional[ModelRegistryArtifact] = None
    """LoRA adapter weights, deployed on top of the base model.

    Set for LoRA training on the base model's own weights.
    """

    model: Optional[ModelRegistryArtifact] = None
    """Full model weights.

    Set for full-weight training, and for LoRA training on custom base weights,
    where the merged model is deployed instead of the adapter.
    """


class InferenceCheckpoint(BaseModel):
    """Saved inference checkpoint"""

    id: str
    """Unique identifier for the checkpoint"""

    created_at: datetime
    """Timestamp when the checkpoint was created"""

    step: Union[str, int]
    """Training step at time of save"""

    registration: Optional[Registration] = None
    """Model registry artifacts to deploy or download this checkpoint from.

    Absent when the checkpoint was not uploaded to the registry.
    """
