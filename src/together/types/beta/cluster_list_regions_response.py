# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["ClusterListRegionsResponse", "Region", "RegionDriverVersion"]


class RegionDriverVersion(BaseModel):
    """
    CUDA/NVIDIA driver versions pair available in the region to use in the create cluster request.
    """

    id: Optional[str] = None
    """Identifier to send as nvidia_version_id in a create request."""

    cuda_version: str
    """CUDA driver version."""

    nvidia_driver_version: str
    """NVIDIA driver version."""

    os: Optional[str] = None
    """Operating system used by this NVIDIA version."""


class Region(BaseModel):
    driver_versions: List[RegionDriverVersion]
    """
    List of supported identifiable cuda/nvidia driver versions pairs available in
    the region.
    """

    name: str
    """Identifiable name of the region."""

    supported_instance_types: List[str]
    """List of supported identifiable gpus available in the region."""


class ClusterListRegionsResponse(BaseModel):
    regions: List[Region]
