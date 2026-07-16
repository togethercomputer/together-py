# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ModelListRevisionsResponse", "Data", "DataValidationError"]


class DataValidationError(BaseModel):
    """One validation error reported for a model revision."""

    message: Optional[str] = None
    """Human-readable validation error message."""

    rule: Optional[str] = None
    """Validation rule that produced the error."""

    severity: Optional[str] = None
    """Severity level reported by the validation rule."""


class Data(BaseModel):
    """Revision metadata for a volume object."""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Timestamp when the revision was created."""

    revision_id: str = FieldInfo(alias="revisionId")
    """Revision identifier."""

    last_validated_at: Optional[datetime] = FieldInfo(alias="lastValidatedAt", default=None)
    """Timestamp when validation most recently ran for the revision."""

    validation_errors: Optional[List[DataValidationError]] = FieldInfo(alias="validationErrors", default=None)
    """Validation errors reported for the revision."""

    validation_status: Optional[
        Literal[
            "REVISION_VALIDATION_STATUS_PENDING",
            "REVISION_VALIDATION_STATUS_SUCCESS",
            "REVISION_VALIDATION_STATUS_FAILED",
            "REVISION_VALIDATION_STATUS_ERROR",
        ]
    ] = FieldInfo(alias="validationStatus", default=None)
    """Current validation status for the revision."""


class ModelListRevisionsResponse(BaseModel):
    """Immutable model revisions and pagination metadata."""

    data: Optional[List[Data]] = None
    """Immutable revisions available for the model."""

    next_cursor: Optional[str] = None
    """Cursor for the next page. Null if there are no more results."""

    object: Optional[Literal["list"]] = None
    """Object type. Always `list`."""
