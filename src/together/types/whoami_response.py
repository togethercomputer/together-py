# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["WhoamiResponse"]


class WhoamiResponse(BaseModel):
    api_key_id: str
    """The ID of the API key that authenticated the request."""

    organization_id: str
    """The ID of the organization that owns the project."""

    organization_name: str
    """Human-readable name of the organization."""

    project_id: str
    """The ID of the project the API key is scoped to."""

    project_name: str
    """Human-readable name of the project."""

    project_slug: str
    """DNS-friendly project identifier.

    Used with an endpoint slug as `<project_slug>/<endpoint_slug>` to form the
    `model` value in dedicated endpoint inference calls.
    """
