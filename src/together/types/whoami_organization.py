# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["WhoamiOrganization"]


class WhoamiOrganization(BaseModel):
    id: str
    """Organization identifier."""

    name: str
    """Organization display name."""
