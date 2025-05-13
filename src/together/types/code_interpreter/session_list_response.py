# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["SessionListResponse", "Data", "DataSession"]


class DataSession(BaseModel):
    id: str
    """Session Identifier. Used to make follow-up calls."""

    execute_count: int

    expires_at: datetime

    last_execute_at: datetime

    started_at: datetime


class Data(BaseModel):
    sessions: List[DataSession]


class SessionListResponse(BaseModel):
    data: Optional[Data] = None

    errors: Optional[List[Union[str, Dict[str, object]]]] = None
