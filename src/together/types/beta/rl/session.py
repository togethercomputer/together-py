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

__all__ = ["Session", "PolicyState"]


class PolicyState(BaseModel):
    """Session-scoped policy and weight versions for this session"""

    applied_weights_version: Union[str, int]
    """Policy version successfully applied to the generator for this session."""

    pending_publish: bool
    """True when a generator publish has been requested but has not finished."""

    target_weights_version: Union[str, int]
    """Policy version promised to the generator by the latest weights-sync."""

    trainer_step: Union[str, int]
    """Policy version produced by the last completed optimizer step.

    Distinct from `TrainingSession.step`, which is the durable optimizer-step
    counter.
    """


class Session(BaseModel):
    """A training session and its current state"""

    id: str
    """ID of the training session"""

    base_model: str
    """Base model the session trains, taken from the model resource it is attached to"""

    created_at: datetime
    """Timestamp when the training session was created"""

    created_by: str
    """ID of the user who created the training session"""

    inference_checkpoints: List[InferenceCheckpoint]
    """List of saved inference checkpoints for this session"""

    metadata: SessionMetadata
    """Auxiliary metadata associated with the training session"""

    resources_id: str = FieldInfo(alias="model_resources_id")
    """ID of the model resource used by this training session."""

    policy_state: PolicyState
    """Session-scoped policy and weight versions for this session"""

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
