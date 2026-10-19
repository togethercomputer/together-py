# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["WhoamiUser"]


class WhoamiUser(BaseModel):
    id: str
    """Authenticated user identifier."""
