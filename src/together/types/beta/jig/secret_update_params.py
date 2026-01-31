# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["SecretUpdateParams"]


class SecretUpdateParams(TypedDict, total=False):
    description: str
    """
    Description is an optional human-readable description of the secret's purpose
    (max 500 characters)
    """

    name: str
    """Name is the new unique identifier for the secret.

    Can contain alphanumeric characters, underscores, hyphens, forward slashes, and
    periods (1-100 characters)
    """

    project_id: str
    """
    ProjectID is ignored - the project is automatically determined from your
    authentication
    """

    value: str
    """Value is the new sensitive data to store securely.

    Updating this will replace the existing secret value
    """
