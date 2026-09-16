# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ResourceUtilization"]


class ResourceUtilization(BaseModel):
    """
    Average compute, memory, and network utilization for replicas over a time range.
    """

    cpu_utilization: Optional[float] = FieldInfo(alias="cpuUtilization", default=None)
    """Average CPU utilization across replicas, as a percentage."""

    gpu_memory_utilization: Optional[float] = FieldInfo(alias="gpuMemoryUtilization", default=None)
    """Average GPU memory utilization across replicas, as a percentage."""

    gpu_utilization: Optional[float] = FieldInfo(alias="gpuUtilization", default=None)
    """Average GPU compute utilization across replicas, as a percentage."""

    memory_utilization: Optional[float] = FieldInfo(alias="memoryUtilization", default=None)
    """Average system memory utilization across replicas, as a percentage."""

    network_bandwidth_mbps: Optional[float] = FieldInfo(alias="networkBandwidthMbps", default=None)
    """Average network throughput across replicas, in megabits per second."""
