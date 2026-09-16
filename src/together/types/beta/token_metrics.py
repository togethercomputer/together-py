# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["TokenMetrics"]


class TokenMetrics(BaseModel):
    """Aggregate and per-request token usage over a time range."""

    avg_input_tokens: Optional[float] = FieldInfo(alias="avgInputTokens", default=None)
    """Average input tokens per request."""

    avg_output_tokens: Optional[float] = FieldInfo(alias="avgOutputTokens", default=None)
    """Average output tokens per request."""

    total_input_tokens: Optional[str] = FieldInfo(alias="totalInputTokens", default=None)
    """Total input tokens processed during the time range."""

    total_output_tokens: Optional[str] = FieldInfo(alias="totalOutputTokens", default=None)
    """Total output tokens generated during the time range."""
