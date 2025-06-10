# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

from .autoscaling_param import AutoscalingParam

__all__ = ["EndpointUpdateParams"]


class EndpointUpdateParams(TypedDict, total=False):
    autoscaling: AutoscalingParam
    """New autoscaling configuration for the endpoint"""

    display_name: str
    """A human-readable name for the endpoint"""

    inactive_timeout: Optional[int]
    """
    The number of minutes of inactivity after which the endpoint will be
    automatically stopped. Set to 0 to disable automatic timeout.
    """

    state: Literal["STARTED", "STOPPED"]
    """The desired state of the endpoint"""
