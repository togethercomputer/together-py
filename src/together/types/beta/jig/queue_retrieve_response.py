# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["QueueRetrieveResponse"]


class QueueRetrieveResponse(BaseModel):
    model: str
    """Model identifier the job was submitted to"""

    request_id: str
    """The request ID that was returned from the submit endpoint"""

    status: Literal["pending", "running", "done", "failed", "canceled"]
    """Current job status.

    Transitions: pending → running → done/failed. A pending job may also be
    canceled.
    """

    claimed_at: Optional[datetime] = None
    """Timestamp when a worker claimed the job"""

    created_at: Optional[datetime] = None
    """Timestamp when the job was created"""

    done_at: Optional[datetime] = None
    """Timestamp when the job completed (done or failed)"""

    info: Optional[Dict[str, object]] = None
    """Job metadata.

    Contains keys from the submit request, plus any modifications from the model or
    system (e.g. progress, retry history).
    """

    inputs: Optional[Dict[str, object]] = None
    """Freeform model input, as submitted"""

    outputs: Optional[Dict[str, object]] = None
    """Freeform model output, populated when the job reaches done status.

    Contents are model-specific.
    """

    priority: Optional[int] = None
    """Job priority. Higher values are processed first."""

    retries: Optional[int] = None
    """Number of times this job has been retried.

    Workers set a claim timeout and must send periodic status updates to keep the
    job alive. If no update is received within the timeout, the job is returned to
    the queue and retried. After 3 retries the job is permanently failed. Jobs
    explicitly failed by the model are not retried.
    """

    warnings: Optional[List[str]] = None
    """Non-fatal messages about the request (e.g. deprecation notices)"""
