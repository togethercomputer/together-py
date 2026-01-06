# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["ClusterStorage"]


class ClusterStorage(BaseModel):
    size_tib: int

    volume_id: str

    volume_name: str
