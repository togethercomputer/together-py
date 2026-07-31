# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .lora_config import LoraConfig
from .training_checkpoint import TrainingCheckpoint
from .inference_checkpoint import InferenceCheckpoint
from .training_session_error import TrainingSessionError
from .training_session_status import TrainingSessionStatus

__all__ = ["TrainingSession", "Metadata", "MetadataWandb"]


class MetadataWandb(BaseModel):
    """Weights & Biases details associated with the training session"""

    entity: Optional[str] = None
    """Weights & Biases username or team that owns the project"""

    group: Optional[str] = None
    """Weights & Biases group used to organize related runs"""

    project: Optional[str] = None
    """Weights & Biases project containing the run"""

    run_id: Optional[str] = None
    """Unique identifier assigned to the run by Weights & Biases"""

    run_name: Optional[str] = None
    """Human-readable name of the Weights & Biases run"""

    url: Optional[str] = None
    """HTTPS URL for the Weights & Biases run"""


class Metadata(BaseModel):
    """Auxiliary metadata associated with the training session"""

    wandb: Optional[MetadataWandb] = None
    """Weights & Biases details associated with the training session"""


class TrainingSession(BaseModel):
    """A training session and its current state"""

    id: str
    """ID of the training session"""

    created_at: datetime
    """Timestamp when the training session was created"""

    created_by: str
    """ID of the user who created the training session"""

    inference_checkpoints: List[InferenceCheckpoint]
    """List of saved inference checkpoints for this session"""

    metadata: Metadata
    """Auxiliary metadata associated with the training session"""

    api_model_resources_id: str = FieldInfo(alias="model_resources_id")
    """Model resource this session is attached to.

    The session runs on that resource's GPU pods.
    """

    status: TrainingSessionStatus
    """Status of the training session"""

    step: Union[str, int]
    """Current training step"""

    training_checkpoints: List[TrainingCheckpoint]
    """List of saved training checkpoints for this session"""

    updated_at: datetime
    """Timestamp when the training session was last updated"""

    display_name: Optional[str] = None
    """Display name used to identify the training session"""

    error: Optional[TrainingSessionError] = None
    """Structured detail for the training session's current error.

    Set when the session is in an error state.
    """

    lora_config: Optional[LoraConfig] = None
    """LoRA adapter configuration.

    Present only for sessions running on a LoRA-enabled model resource.
    """

    resume_from_checkpoint_id: Optional[str] = None
    """Checkpoint ID this session was resumed from"""
