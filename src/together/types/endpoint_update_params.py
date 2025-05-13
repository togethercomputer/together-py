# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["EndpointUpdateParams", "Autoscaling"]


class EndpointUpdateParams(TypedDict, total=False):
    autoscaling: Autoscaling
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


class Autoscaling(TypedDict, total=False):
    max_replicas: Required[int]
    """The maximum number of replicas to scale up to under load"""

    min_replicas: Required[int]
    """The minimum number of replicas to maintain, even when there is no load"""
