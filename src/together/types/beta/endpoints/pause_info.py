# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["PauseInfo"]


class PauseInfo(BaseModel):
    """Pause metadata returned while a rollout is paused."""

    paused_at: datetime = FieldInfo(alias="pausedAt")
    """Timestamp when the rollout was paused."""

    reason: Optional[str] = None
    """Human-readable reason recorded when the rollout was paused."""
