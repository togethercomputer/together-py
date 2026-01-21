# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["ClusterStorage"]


class ClusterStorage(BaseModel):
    size_tib: int

    status: Literal["available", "bound", "provisioning"]

    volume_id: str

    volume_name: str
