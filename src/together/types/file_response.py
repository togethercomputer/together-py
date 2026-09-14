# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .file_type import FileType
from .file_purpose import FilePurpose

__all__ = ["FileResponse", "ValidationReport"]


class ValidationReport(BaseModel):
    """Report produced by the file validation pipeline.

    Present once
    validation has run; absent on files that bypassed validation
    (non-`fine-tune` purposes) or have not yet been validated.
    """

    valid: bool
    """Whether the file passed validation."""

    dataset_format: Optional[str] = None
    """Detected dataset format (e.g. `CONVERSATION`, `INSTRUCTION`)."""

    dataset_has_message_weights: Optional[bool] = None
    """
    Whether the dataset carries per-message weights (only possible for
    `CONVERSATION` format).
    """

    dataset_has_parallel_tool_calls: Optional[bool] = None
    """Whether the dataset contains parallel tool-use messages."""

    dataset_has_reasoning: Optional[bool] = None
    """Whether the dataset contains reasoning content."""

    dataset_has_sample_weights: Optional[bool] = None
    """Whether the dataset carries per-sample weights."""

    dataset_has_tools: Optional[bool] = None
    """Whether the dataset contains tool-use messages."""

    dataset_is_multimodal: Optional[bool] = None
    """Whether the dataset contains multimodal content."""

    error: Optional[str] = None
    """Human-readable validation error message.

    Only present when `error_type` is set (i.e. user-correctable failures).
    """

    error_type: Optional[Literal["INVALID_FORMAT"]] = None
    """Category of validation failure."""

    file_id: Optional[str] = None
    """ID of the file this report describes."""

    nlines: Optional[int] = None
    """Number of lines (records) in the dataset."""


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
    """Deprecated. Whether file has been fully uploaded."""

    purpose: FilePurpose
    """The purpose of the file as it was uploaded."""

    processing_status: Optional[Literal["PENDING", "QUEUED", "RUNNING", "COMPLETED", "FAILED", "INVALID_FORMAT"]] = None
    """Lifecycle state of the file validation pipeline.

    Files for non-`fine-tune` purposes skip validation.
    """

    validation_report: Optional[ValidationReport] = None
    """Report produced by the file validation pipeline.

    Present once validation has run; absent on files that bypassed validation
    (non-`fine-tune` purposes) or have not yet been validated.
    """
