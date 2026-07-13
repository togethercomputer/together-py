# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from datetime import datetime

from ...._models import BaseModel

__all__ = ["TrainingCheckpoint"]


class TrainingCheckpoint(BaseModel):
    """Saved training checkpoint"""

    id: str
    """Unique identifier for the checkpoint"""

    created_at: datetime
    """Timestamp when the checkpoint was created"""

    step: Union[str, int]
    """Training step at time of save"""
