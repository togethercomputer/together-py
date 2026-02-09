# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["QueueCancelResponse"]


class QueueCancelResponse(BaseModel):
    status: Literal["canceled", "running", "done", "failed"]
    """Job status after the cancel attempt.

    Only pending jobs can be canceled. If the job is already running, done, or
    failed, the status is returned unchanged.
    """
