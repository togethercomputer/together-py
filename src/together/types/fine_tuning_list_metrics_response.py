# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel

__all__ = ["FineTuningListMetricsResponse"]


class FineTuningListMetricsResponse(BaseModel):
    metrics: Optional[List[Dict[str, float]]] = None
