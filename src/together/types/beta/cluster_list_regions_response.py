# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel

__all__ = ["ClusterListRegionsResponse", "Region", "RegionDriverVersion"]


class RegionDriverVersion(BaseModel):
    """NVIDIA software configuration available in the region."""

    id: str
    """
    Region-specific NVIDIA catalog ID to send as nvidia_version_id when creating a
    cluster.
    """

    cuda_version: str
    """Semantic CUDA version without operating system text."""

    nvidia_driver_version: str
    """NVIDIA driver version."""

    os: str
    """Operating system image family for this catalog entry."""


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
