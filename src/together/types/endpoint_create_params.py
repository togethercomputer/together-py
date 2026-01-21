# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

from .autoscaling_param import AutoscalingParam

__all__ = ["EndpointCreateParams"]


class EndpointCreateParams(TypedDict, total=False):
    autoscaling: Required[AutoscalingParam]
    """Configuration for automatic scaling of the endpoint"""

    hardware: Required[str]
    """The hardware configuration to use for this endpoint"""

    model: Required[str]
    """The model to deploy on this endpoint"""

    availability_zone: str
    """Create the endpoint in a specified availability zone (e.g., us-central-4b)"""

    disable_prompt_cache: bool
    """This parameter is deprecated and no longer has any effect."""

    disable_speculative_decoding: bool
    """Whether to disable speculative decoding for this endpoint"""

    display_name: str
    """A human-readable name for the endpoint"""

    inactive_timeout: Optional[int]
    """
    The number of minutes of inactivity after which the endpoint will be
    automatically stopped. Set to null, omit or set to 0 to disable automatic
    timeout.
    """

    state: Literal["STARTED", "STOPPED"]
    """The desired state of the endpoint"""
