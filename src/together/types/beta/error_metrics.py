# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ErrorMetrics"]


class ErrorMetrics(BaseModel):
    """Error rate and aggregate counts by error type.

    Individual error samples are not included.
    """

    error_rate: Optional[float] = FieldInfo(alias="errorRate", default=None)
    """Percentage in [0, 100]."""

    errors_by_type: Optional[Dict[str, str]] = FieldInfo(alias="errorsByType", default=None)
    """Counts of errors keyed by error type (e.g. HTTP status code or error kind)."""
