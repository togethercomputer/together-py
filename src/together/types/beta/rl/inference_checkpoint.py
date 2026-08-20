# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["InferenceCheckpoint", "Registration"]


class Registration(BaseModel):
    """Model registration details"""

    registered_model_name: str = FieldInfo(alias="model_name")
    """Registered model name for downloading the checkpoint"""

    registered_at: datetime
    """Timestamp when the model was registered"""

    adapter_object_id: Optional[str] = None
    """Together model registry object ID for the adapter checkpoint (e.g.

    `ml_...`), set on LoRA training sessions
    """

    adapter_object_revision_id: Optional[str] = None
    """Together model registry revision ID for the adapter checkpoint (e.g. `rv_...`)"""

    api_model_object_id: Optional[str] = FieldInfo(alias="model_object_id", default=None)
    """Together model registry object ID for the model checkpoint (e.g.

    `ml_...`), set on full-weight training sessions
    """

    api_model_object_revision_id: Optional[str] = FieldInfo(alias="model_object_revision_id", default=None)
    """Together model registry revision ID for the model checkpoint (e.g. `rv_...`)"""


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
