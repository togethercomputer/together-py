# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from ...._models import BaseModel

__all__ = ["QueueRetrieveResponse"]


class QueueRetrieveResponse(BaseModel):
    claimed_at: Optional[str] = None

    created_at: Optional[str] = None

    done_at: Optional[str] = None

    info: Optional[Dict[str, object]] = None

    inputs: Optional[Dict[str, object]] = None

    model: Optional[str] = None

    outputs: Optional[Dict[str, object]] = None

    priority: Optional[int] = None
    """Additional fields for test compatibility"""

    request_id: Optional[str] = None

    retries: Optional[int] = None

    status: Optional[str] = None
    """this should be the enum, but isn't for backwards compatability"""

    warnings: Optional[List[str]] = None
