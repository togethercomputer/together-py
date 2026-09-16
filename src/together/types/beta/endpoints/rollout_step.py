# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["RolloutStep"]


class RolloutStep(BaseModel):
    """One stage of a canary rollout progression."""

    traffic: int
    """Required percentage of traffic on the target deployment for this step."""

    replicas: Optional[int] = None
    """Optional explicit target replica count for this step."""
