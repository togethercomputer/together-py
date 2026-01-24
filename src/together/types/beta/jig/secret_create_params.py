# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["SecretCreateParams"]


class SecretCreateParams(TypedDict, total=False):
    name: Required[str]
    """Name is the unique identifier for the secret.

    Can contain alphanumeric characters, underscores, hyphens, forward slashes, and
    periods (1-100 characters)
    """

    value: Required[str]
    """
    Value is the sensitive data to store securely (e.g., API keys, passwords,
    tokens). This value will be encrypted at rest
    """

    description: str
    """
    Description is an optional human-readable description of the secret's purpose
    (max 500 characters)
    """

    project_id: str
    """
    ProjectID is ignored - the project is automatically determined from your
    authentication
    """
