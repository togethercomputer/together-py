# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime

from .._models import BaseModel

__all__ = ["FineTuneTokenizedDatasetRetrieveResponse"]


class FineTuneTokenizedDatasetRetrieveResponse(BaseModel):
    """Presigned download metadata for a fine-tune tokenized dataset archive."""

    content_type: str
    """MIME type for the tokenized dataset archive."""

    expires_at: datetime
    """Time when the presigned download URL expires."""

    filename: str
    """Archive filename to use when saving the downloaded tokenized dataset."""

    size: int
    """Archive size in bytes."""

    url: str
    """Presigned URL for downloading the tokenized dataset archive."""
