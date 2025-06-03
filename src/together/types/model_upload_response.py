# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ModelUploadResponse", "Data"]


class Data(BaseModel):
    job_id: str

    x_model_id: str = FieldInfo(alias="model_id")

    x_model_name: str = FieldInfo(alias="model_name")

    x_model_source: str = FieldInfo(alias="model_source")


class ModelUploadResponse(BaseModel):
    data: Data

    message: str
