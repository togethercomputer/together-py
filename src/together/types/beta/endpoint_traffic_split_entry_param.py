# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["EndpointTrafficSplitEntryParam"]


class EndpointTrafficSplitEntryParam(TypedDict, total=False):
    """Capacity weight assigned to one deployment in an endpoint's live traffic split."""

    deployment_id: Required[Annotated[str, PropertyInfo(alias="deploymentId")]]
    """ID of a deployment under the endpoint that can receive live traffic."""

    weight: Required[float]
    """Non-negative, finite weight applied to each ready replica.

    A deployment's effective routing capacity is `weight * readyReplicas`, and
    requests are distributed in proportion to that capacity. Set to `0` to remove
    the deployment from the live traffic split.
    """
