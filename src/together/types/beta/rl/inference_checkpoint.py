# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["InferenceCheckpoint", "Registration"]


class Registration(BaseModel):
    """Model registration details"""

    api_model_name: str = FieldInfo(alias="model_name")
    """Registered model name for downloading the checkpoint"""

    registered_at: datetime
    """Timestamp when the model was registered"""


class InferenceCheckpoint(BaseModel):
    """Saved inference checkpoint"""

    id: str
    """Unique identifier for the checkpoint"""

    created_at: datetime
    """Timestamp when the checkpoint was created"""

    step: Union[str, int]
    """Training step at time of save"""

    registration: Optional[Registration] = None
    """Model registration details"""
