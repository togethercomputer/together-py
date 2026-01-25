# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["Secret"]


class Secret(BaseModel):
    id: Optional[str] = None
    """ID is the unique identifier for this secret"""

    created_at: Optional[str] = None
    """CreatedAt is the ISO8601 timestamp when this secret was created"""

    created_by: Optional[str] = None
    """CreatedBy is the identifier of the user who created this secret"""

    description: Optional[str] = None
    """Description is a human-readable description of the secret's purpose"""

    last_updated_by: Optional[str] = None
    """LastUpdatedBy is the identifier of the user who last updated this secret"""

    name: Optional[str] = None
    """Name is the name/key of the secret"""

    object: Optional[str] = None
    """Object is the type identifier for this response (always "secret")"""

    updated_at: Optional[str] = None
    """UpdatedAt is the ISO8601 timestamp when this secret was last updated"""
