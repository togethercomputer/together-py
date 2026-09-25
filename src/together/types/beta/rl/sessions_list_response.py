# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .session import Session
from ...._models import BaseModel

__all__ = ["SessionsListResponse", "Meta"]


class Meta(BaseModel):
    """Pagination metadata"""

    has_more: Optional[bool] = None
    """Whether more items exist beyond this page"""

    limit: Optional[int] = None
    """Maximum number of items returned per page"""

    next_cursor: Optional[str] = None
    """Cursor to use as the 'after' parameter for the next page.

    Empty when has_more is false.
    """


class SessionsListResponse(BaseModel):
    """Paginated list of training sessions"""

    data: Optional[List[Session]] = None
    """List of training sessions"""

    meta: Optional[Meta] = None
    """Pagination metadata"""
