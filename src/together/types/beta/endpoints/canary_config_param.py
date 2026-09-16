# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo
from .rollout_step_param import RolloutStepParam

__all__ = ["CanaryConfigParam"]


class CanaryConfigParam(TypedDict, total=False):
    """Canary strategy configuration for gradual traffic progression.

    An empty config uses the default 5, 25, 50, 100 percent ladder; over a frozen traffic-split pair left by cancel, the default ladder is derived at start from the pair's current served share so it begins above it.
    """

    step_interval: Annotated[str, PropertyInfo(alias="stepInterval")]
    """Optional positive soak between steps.

    Defaults to 3m if omitted, and grows to cover metric rule windows plus ingestion
    lag.
    """

    steps: Iterable[RolloutStepParam]
    """Optional progression steps.

    Defaults to 5, 25, 50, 100 percent when empty; explicit steps must increase and
    end at 100 percent.
    """
