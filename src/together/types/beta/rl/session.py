# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .lora_config import LoraConfig
from .session_error import SessionError
from .session_status import SessionStatus
from .session_metadata import SessionMetadata
from .training_checkpoint import TrainingCheckpoint
from .inference_checkpoint import InferenceCheckpoint

__all__ = ["Session"]


class Session(BaseModel):
    """A training session and its current state"""

    id: str
    """ID of the training session"""

    created_at: datetime
    """Timestamp when the training session was created"""

    created_by: str
    """ID of the user who created the training session"""

    inference_checkpoints: List[InferenceCheckpoint]
    """List of saved inference checkpoints for this session"""

    metadata: SessionMetadata
    """Auxiliary metadata associated with the training session"""

    resources_id: str = FieldInfo(alias="model_resources_id")
    """Model resource this session is attached to.

    The session runs on that resource's GPU pods.
    """

    status: SessionStatus
    """Status of the training session"""

    step: Union[str, int]
    """Current training step"""

    training_checkpoints: List[TrainingCheckpoint]
    """List of saved training checkpoints for this session"""

    updated_at: datetime
    """Timestamp when the training session was last updated"""

    display_name: Optional[str] = None
    """Display name used to identify the training session"""

    error: Optional[SessionError] = None
    """Structured detail for the training session's current error.

    Set when the session is in an error state.
    """

    lora_config: Optional[LoraConfig] = None
    """LoRA adapter configuration.

    Present only for sessions running on a LoRA-enabled model resource.
    """

    resume_from_checkpoint_id: Optional[str] = None
    """Checkpoint ID this session was resumed from"""
