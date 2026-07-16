# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["RemoteUploadRetrieveResponse"]


class RemoteUploadRetrieveResponse(BaseModel):
    """
    Asynchronous job that imports remote files into a registered model and creates a model revision.
    """

    id: str
    """Unique ID of the remote model import job."""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Time when the import job was created."""

    api_model_id: str = FieldInfo(alias="modelId")
    """ID of the registered model receiving the imported files."""

    project_id: str = FieldInfo(alias="projectId")
    """ID of the project that owns the import job."""

    remote_url: str = FieldInfo(alias="remoteUrl")
    """Hugging Face repository or presigned URL being imported."""

    status: Literal[
        "REMOTE_UPLOAD_STATUS_PENDING",
        "REMOTE_UPLOAD_STATUS_RUNNING",
        "REMOTE_UPLOAD_STATUS_ERROR",
        "REMOTE_UPLOAD_STATUS_SUCCEEDED",
        "REMOTE_UPLOAD_STATUS_FAILED",
    ]
    """Current lifecycle state of the asynchronous import job."""

    max_restarts: Optional[int] = FieldInfo(alias="maxRestarts", default=None)
    """Maximum worker restarts allowed before the job fails permanently."""

    restart_count: Optional[int] = FieldInfo(alias="restartCount", default=None)
    """Number of times the import worker has restarted this job."""

    status_message: Optional[str] = FieldInfo(alias="statusMessage", default=None)
    """Human-readable progress or failure detail for the current status."""

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)
    """Time when the import job was last updated."""
