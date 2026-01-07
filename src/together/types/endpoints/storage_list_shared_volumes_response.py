# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel
from ..beta.clusters.cluster_storage import ClusterStorage

__all__ = ["StorageListSharedVolumesResponse"]


class StorageListSharedVolumesResponse(BaseModel):
    volumes: List[ClusterStorage]
