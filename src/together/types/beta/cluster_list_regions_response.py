# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel

__all__ = ["ClusterListRegionsResponse", "Region", "RegionDriverVersion"]


class RegionDriverVersion(BaseModel):
    """
    CUDA/NVIDIA driver versions pair available in the region to use in the create cluster request.
    """

    cuda_version: str
    """CUDA driver version."""

    nvidia_driver_version: str
    """NVIDIA driver version."""


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
