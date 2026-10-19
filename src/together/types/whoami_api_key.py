# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["WhoamiAPIKey"]


class WhoamiAPIKey(BaseModel):
    id: str
    """The authenticated API key identifier."""
