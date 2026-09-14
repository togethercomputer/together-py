# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .batch_job import BatchJob

__all__ = ["BatchCreateResponse"]


class BatchCreateResponse(BaseModel):
    job: Optional[BatchJob] = None

    warning: Optional[str] = None
