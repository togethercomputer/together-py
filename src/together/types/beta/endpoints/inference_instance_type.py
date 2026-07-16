# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["InferenceInstanceType", "Region", "RegionHeadroom"]


class RegionHeadroom(BaseModel):
    """Best-effort estimate of how many additional replicas currently fit in a region."""

    relation: Literal["RELATION_EQ", "RELATION_GTE"]
    """Whether the value is exact or a lower bound."""

    value: Optional[int] = None
    """Capped count of replicas that currently fit."""


class Region(BaseModel):
    """Region where an instance type is offered."""

    name: str
    """Region name where an instance type is offered."""

    headroom: Optional[RegionHeadroom] = None
    """Best-effort estimate of how many additional replicas currently fit in a region."""


class InferenceInstanceType(BaseModel):
    """GPU hardware configuration on which one inference replica can run."""

    id: str
    """Stable hardware instance type identifier used by deployment configs."""

    description: str
    """Human-readable summary of the hardware configuration."""

    gpu_count: int = FieldInfo(alias="gpuCount")
    """Number of GPUs in one replica of this instance type."""

    gpu_memory_gib: int = FieldInfo(alias="gpuMemoryGib")
    """Memory available on each GPU, in GiB."""

    gpu_type: str = FieldInfo(alias="gpuType")
    """GPU accelerator model, such as `H100` or `B200`."""

    name: str
    """Human-readable instance type name."""

    price_cents_per_hour: int = FieldInfo(alias="priceCentsPerHour")
    """On-demand price for one running replica, in US cents per hour."""

    regions: List[Region]
    """Regions where this instance type is offered."""
