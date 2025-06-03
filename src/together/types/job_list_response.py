# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["JobListResponse", "Data", "DataArgs", "DataStatusUpdate"]


class DataArgs(BaseModel):
    description: Optional[str] = None

    x_model_name: Optional[str] = FieldInfo(alias="modelName", default=None)

    x_model_source: Optional[str] = FieldInfo(alias="modelSource", default=None)


class DataStatusUpdate(BaseModel):
    message: str

    status: str

    timestamp: datetime


class Data(BaseModel):
    args: DataArgs

    created_at: datetime

    job_id: str

    status: Literal["Queued", "Running", "Complete", "Failed"]

    status_updates: List[DataStatusUpdate]

    type: str

    updated_at: datetime


class JobListResponse(BaseModel):
    data: List[Data]
