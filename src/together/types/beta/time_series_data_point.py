# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["TimeSeriesDataPoint"]


class TimeSeriesDataPoint(BaseModel):
    """Timestamped bucket containing one or more named metric values."""

    timestamp: Optional[datetime] = None
    """Start time of the metric bucket."""

    values: Optional[Dict[str, float]] = None
    """Metric names mapped to their numeric values for this bucket."""
