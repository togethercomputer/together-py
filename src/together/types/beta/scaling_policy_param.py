# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ScalingPolicyParam"]


class ScalingPolicyParam(TypedDict, total=False):
    """Replica rate-limit policy applied over a trailing window."""

    period_seconds: Required[Annotated[int, PropertyInfo(alias="periodSeconds")]]
    """Trailing rate-limit window in seconds, from 1 to 1800."""

    type: Required[Literal["SCALING_POLICY_TYPE_PODS", "SCALING_POLICY_TYPE_PERCENT"]]
    """
    Whether `value` is a replica count or a percentage of the replica count at the
    start of the trailing period. Scaling events within that period count against
    the allowance; percentages are rounded to whole replicas.
    """

    value: Required[int]
    """Positive replica count or percentage used as the rate-limit amount."""
