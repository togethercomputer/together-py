# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .lora_config import LoraConfig
from .training_checkpoint import TrainingCheckpoint
from .inference_checkpoint import InferenceCheckpoint
from .training_session_status import TrainingSessionStatus

__all__ = ["TrainingSession", "Error"]


class Error(BaseModel):
    """Structured detail for the training session's current error.

    Set when the session is in an error state.
    """

    code: Literal[
        "TRAINING_SESSION_ERROR_CODE_RESOURCE_UNAVAILABLE",
        "TRAINING_SESSION_ERROR_CODE_RESOURCE_AT_CAPACITY",
        "TRAINING_SESSION_ERROR_CODE_TIMED_OUT",
        "TRAINING_SESSION_ERROR_CODE_SESSION_FAILED",
    ]
    """Finite machine-readable reason code for UI branching"""

    message: str
    """User-safe human-readable detail for the current status"""

    occurred_at: datetime
    """Timestamp when this error was reported"""


class TrainingSession(BaseModel):
    """A training session and its current state"""

    id: str
    """ID of the training session"""

    created_at: datetime
    """Timestamp when the training session was created"""

    inference_checkpoints: List[InferenceCheckpoint]
    """List of saved inference checkpoints for this session"""

    lora_config: LoraConfig
    """LoRA adapter configuration for this session"""

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

    error: Optional[Error] = None
    """Structured detail for the training session's current error.

    Set when the session is in an error state.
    """

    resume_from_checkpoint_id: Optional[str] = None
    """Checkpoint ID this session was resumed from"""
