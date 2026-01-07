# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel
from .beta.cluster import Cluster

__all__ = ["EndpointListClustersResponse"]


class EndpointListClustersResponse(BaseModel):
    clusters: List[Cluster]
