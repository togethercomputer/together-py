# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .file_type import FileType
from .file_purpose import FilePurpose

__all__ = ["FileResponse"]


class FileResponse(BaseModel):
    id: str

    bytes: int

    created_at: int

    filename: str

    file_type: FileType = FieldInfo(alias="FileType")
    """The type of the file"""

    line_count: int = FieldInfo(alias="LineCount")

    object: str

    processed: bool = FieldInfo(alias="Processed")

    purpose: FilePurpose
    """The purpose of the file"""
