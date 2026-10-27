# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["Secret"]


class Secret(BaseModel):
    id: Optional[str] = None
    """ID is the unique identifier for this secret"""

    created_at: Optional[str] = None
    """CreatedAt is the ISO8601 timestamp when this secret was created"""

    created_by: Optional[str] = None
    """CreatedBy is the identifier of who created this secret."""

    description: Optional[str] = None
    """Description is a human-readable description of the secret's purpose"""

    expires_at: Optional[datetime] = None
    """ExpiresAt is the ISO8601 timestamp when this secret expires and is deleted.

    Changing the value extends it. Omitted for secrets that never expire
    """

    last_updated_by: Optional[str] = None
    """LastUpdatedBy is the identifier of who last updated this secret."""

    name: Optional[str] = None
    """Name is the name/key of the secret"""

    object: Optional[Literal["secret"]] = None
    """The object type, which is always `secret`."""

    ttl_seconds: Optional[int] = None
    """TTLSeconds is the secret's lifetime in seconds. Omitted when no TTL is set"""

    updated_at: Optional[str] = None
    """UpdatedAt is the ISO8601 timestamp when this secret was last updated"""
