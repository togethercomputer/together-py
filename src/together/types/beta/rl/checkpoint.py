# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from datetime import datetime

from ...._models import BaseModel
from .checkpoint_type import CheckpointType

__all__ = ["Checkpoint"]


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
    """Whether this is a training checkpoint or an inference checkpoint"""

    lora_rank: Optional[int] = None
    """LoRA rank of the session that produced this checkpoint.

    Absent for full-weight sessions and for checkpoints saved before this field was
    recorded.
    """
