# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["FileListResponse", "Data"]


class Data(BaseModel):
    id: str

    bytes: int

    created_at: int

    filename: str

    file_type: str = FieldInfo(alias="FileType")

    line_count: int = FieldInfo(alias="LineCount")

    object: str

    processed: bool = FieldInfo(alias="Processed")

    purpose: str


class FileListResponse(BaseModel):
    data: List[Data]
