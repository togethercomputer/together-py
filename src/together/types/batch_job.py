# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["BatchJob"]


class BatchJob(BaseModel):
    id: Optional[str] = None

    completed_at: Optional[datetime] = None

    created_at: Optional[datetime] = None

    endpoint: Optional[str] = None

    error: Optional[str] = None

    error_file_id: Optional[str] = None

    file_size_bytes: Optional[int] = None
    """Size of input file in bytes"""

    input_file_id: Optional[str] = None

    job_deadline: Optional[datetime] = None

    x_model_id: Optional[str] = FieldInfo(alias="model_id", default=None)
    """Model used for processing requests"""

    output_file_id: Optional[str] = None

    progress: Optional[float] = None
    """Completion progress (0.0 to 100)"""

    status: Optional[Literal["VALIDATING", "IN_PROGRESS", "COMPLETED", "FAILED", "EXPIRED", "CANCELLED"]] = None
    """Current status of the batch job"""

    user_id: Optional[str] = None
