# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ScalingPolicy"]


class ScalingPolicy(BaseModel):
    """Replica rate-limit policy applied over a trailing window."""

    period_seconds: int = FieldInfo(alias="periodSeconds")
    """Trailing rate-limit window in seconds, from 1 to 1800."""

    type: Literal["SCALING_POLICY_TYPE_PODS", "SCALING_POLICY_TYPE_PERCENT"]
    """
    Whether `value` is a replica count or a percentage of the replica count at the
    start of the trailing period. Scaling events within that period count against
    the allowance; percentages are rounded to whole replicas.
    """

    value: int
    """Positive replica count or percentage used as the rate-limit amount."""
