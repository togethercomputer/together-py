# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .rollout_step import RolloutStep

__all__ = ["CanaryConfig"]


class CanaryConfig(BaseModel):
    """Canary strategy configuration for gradual traffic progression.

    An empty config uses the default 5, 25, 50, 100 percent ladder; over a frozen traffic-split pair left by cancel, the default ladder is derived at start from the pair's current served share so it begins above it.
    """

    step_interval: Optional[str] = FieldInfo(alias="stepInterval", default=None)
    """Optional positive soak between steps.

    Defaults to 3m if omitted, and grows to cover metric rule windows plus ingestion
    lag.
    """

    steps: Optional[List[RolloutStep]] = None
    """Optional progression steps.

    Defaults to 5, 25, 50, 100 percent when empty; explicit steps must increase and
    end at 100 percent.
    """
