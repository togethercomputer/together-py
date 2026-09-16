# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["RolloutStepParam"]


class RolloutStepParam(TypedDict, total=False):
    """One stage of a canary rollout progression."""

    traffic: Required[int]
    """Required percentage of traffic on the target deployment for this step."""

    replicas: int
    """Optional explicit target replica count for this step."""
