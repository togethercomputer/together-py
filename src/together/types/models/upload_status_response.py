# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["UploadStatusResponse", "Args", "StatusUpdate"]


class Args(BaseModel):
    description: Optional[str] = None

    x_model_name: Optional[str] = FieldInfo(alias="modelName", default=None)

    x_model_source: Optional[str] = FieldInfo(alias="modelSource", default=None)


class StatusUpdate(BaseModel):
    message: str

    status: str

    timestamp: datetime


class UploadStatusResponse(BaseModel):
    args: Args

    created_at: datetime

    job_id: str

    status: Literal["Queued", "Running", "Complete", "Failed"]

    status_updates: List[StatusUpdate]

    type: str

    updated_at: datetime
