# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo
from .endpoint_traffic_split_entry_param import EndpointTrafficSplitEntryParam

__all__ = ["EndpointUpdateParams"]


class EndpointUpdateParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    update_mask: Annotated[str, PropertyInfo(alias="updateMask")]
    """Fields to update. If not set, the fields populated are updated."""

    etag: str
    """Current endpoint version.

    The update is rejected if this value no longer matches.
    """

    name: str
    """Updated endpoint string."""

    traffic_split: Annotated[Iterable[EndpointTrafficSplitEntryParam], PropertyInfo(alias="trafficSplit")]
    """Replacement live traffic split. Use an empty list to stop routing live traffic."""

    visibility: Literal["VISIBILITY_PRIVATE", "VISIBILITY_INTERNAL"]
    """Who can discover the endpoint.

    `VISIBILITY_PRIVATE` restricts it to the project; `VISIBILITY_INTERNAL` shares
    it with the organization.
    """
