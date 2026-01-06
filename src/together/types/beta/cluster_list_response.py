# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .cluster import Cluster
from ..._models import BaseModel

__all__ = ["ClusterListResponse"]


class ClusterListResponse(BaseModel):
    clusters: List[Cluster]
