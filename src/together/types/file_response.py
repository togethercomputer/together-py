# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .file_type import FileType
from .file_purpose import FilePurpose

__all__ = ["FileResponse"]


class FileResponse(BaseModel):
    """Structured information describing a file uploaded to Together."""

    id: str
    """ID of the file."""

    bytes: int
    """The number of bytes in the file."""

    created_at: int
    """The timestamp when the file was created."""

    filename: str
    """The name of the file as it was uploaded."""

    file_type: FileType = FieldInfo(alias="FileType")
    """The type of the file such as `jsonl`, `csv`, or `parquet`."""

    object: Literal["file"]
    """The object type, which is always `file`."""

    processed: bool = FieldInfo(alias="Processed")
    """Whether the file has been parsed and analyzed for correctness for fine-tuning."""

    purpose: FilePurpose
    """The purpose of the file as it was uploaded."""
