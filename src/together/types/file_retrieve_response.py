# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["FileRetrieveResponse"]


class FileRetrieveResponse(BaseModel):
    id: str

    bytes: int

    created_at: int

    filename: str

    file_type: Literal["jsonl", "parquet"] = FieldInfo(alias="FileType")

    line_count: int = FieldInfo(alias="LineCount")

    object: str

    processed: bool = FieldInfo(alias="Processed")

    purpose: Literal["fine-tune"]
