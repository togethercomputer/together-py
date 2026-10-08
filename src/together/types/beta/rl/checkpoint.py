# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from datetime import datetime

from ...._models import BaseModel
from .checkpoint_type import CheckpointType
from .model_registry_artifact import ModelRegistryArtifact

__all__ = ["Checkpoint", "InferenceRegistration"]


class InferenceRegistration(BaseModel):
    """Model registry artifacts to deploy or download this inference checkpoint from.

    Absent for training checkpoints and when the checkpoint was not uploaded to the registry.
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


class Checkpoint(BaseModel):
    """Metadata for a saved checkpoint"""

    id: str
    """Unique identifier for the checkpoint"""

    base_model: str
    """Base model the checkpoint was trained from"""

    created_at: datetime
    """Timestamp when the checkpoint was created"""

    session_id: str
    """Training session that produced the checkpoint"""

    step: Union[str, int]
    """Training step at time of save"""

    type: CheckpointType
    """Kind of checkpoint.

    CHECKPOINT_TYPE_TRAINING is the full training state (weights and optimizer
    state), for resuming a training session with its optimizer state;
    CHECKPOINT_TYPE_INFERENCE is a model ready for serving or download, also added
    to your models.
    """

    inference_registration: Optional[InferenceRegistration] = None
    """Model registry artifacts to deploy or download this inference checkpoint from.

    Absent for training checkpoints and when the checkpoint was not uploaded to the
    registry.
    """

    lora_rank: Optional[int] = None
    """LoRA rank of the session that produced this checkpoint.

    Absent for full-weight sessions and for checkpoints saved before this field was
    recorded.
    """

    training_registration: Optional[ModelRegistryArtifact] = None
    """
    Model registry artifact holding this training checkpoint's training state, used
    to resume training rather than to deploy. Absent for inference checkpoints and
    when the checkpoint was not uploaded to the registry.
    """
