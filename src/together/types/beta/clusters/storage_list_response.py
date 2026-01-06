# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ...._models import BaseModel
from .cluster_storage import ClusterStorage

__all__ = ["StorageListResponse"]


class StorageListResponse(BaseModel):
    volumes: List[ClusterStorage]
