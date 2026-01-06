# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel

__all__ = ["ClusterListRegionsResponse", "Region"]


class Region(BaseModel):
    id: str

    availability_zones: List[str]

    driver_versions: List[str]

    name: str


class ClusterListRegionsResponse(BaseModel):
    regions: List[Region]
