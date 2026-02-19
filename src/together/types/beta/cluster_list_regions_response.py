# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["ClusterListRegionsResponse", "Region"]


class Region(BaseModel):
    driver_versions: List[str]
    """List of supported identifiable driver versions available in the region."""

    name: str
    """Identifiable name of the region."""

    supported_instance_types: Optional[List[str]] = None
    """List of supported identifiable gpus available in the region."""


class ClusterListRegionsResponse(BaseModel):
    regions: List[Region]
