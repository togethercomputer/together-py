# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .session_metadata_param import SessionMetadataParam

__all__ = ["SessionUpdateParams"]


class SessionUpdateParams(TypedDict, total=False):
    display_name: str
    """Display name to update. An empty string clears the existing display name."""

    metadata: SessionMetadataParam
    """Metadata fields to update.

    Omitted fields remain unchanged, and empty strings clear existing values.
    """
