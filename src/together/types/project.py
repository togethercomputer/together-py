# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["Project"]


class Project(BaseModel):
    """A project the authenticated caller can access."""

    id: str
    """Unique project identifier."""

    name: str
    """Display name of the project."""

    organization_id: str
    """ID of the organization that owns the project."""

    organization_name: str
    """Display name of the organization that owns the project."""

    slug: str
    """Customer-facing project slug."""
