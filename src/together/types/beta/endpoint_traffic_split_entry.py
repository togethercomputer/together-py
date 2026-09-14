# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["EndpointTrafficSplitEntry"]


class EndpointTrafficSplitEntry(BaseModel):
    """Capacity weight assigned to one deployment in an endpoint's live traffic split."""

    deployment_id: str = FieldInfo(alias="deploymentId")
    """ID of a deployment under the endpoint that can receive live traffic."""

    weight: float
    """Non-negative, finite weight applied to each ready replica.

    A deployment's effective routing capacity is `weight * readyReplicas`, and
    requests are distributed in proportion to that capacity. Set to `0` to remove
    the deployment from the live traffic split.
    """
