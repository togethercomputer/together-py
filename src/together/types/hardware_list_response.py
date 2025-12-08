# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["HardwareListResponse", "Data", "DataPricing", "DataSpecs", "DataAvailability"]


class DataPricing(BaseModel):
    """Pricing details for using an endpoint"""

    cents_per_minute: float
    """Cost per minute of endpoint uptime in cents"""


class DataSpecs(BaseModel):
    """Detailed specifications of a hardware configuration"""

    gpu_count: int
    """Number of GPUs in this configuration"""

    gpu_link: str
    """The GPU interconnect technology"""

    gpu_memory: float
    """Amount of GPU memory in GB"""

    gpu_type: str
    """The type/model of GPU"""


class DataAvailability(BaseModel):
    """Indicates the current availability status of a hardware configuration"""

    status: Literal["available", "unavailable", "insufficient"]
    """The availability status of the hardware configuration"""


class Data(BaseModel):
    """Hardware configuration details with optional availability status"""

    id: str
    """Unique identifier for the hardware configuration"""

    object: Literal["hardware"]

    pricing: DataPricing
    """Pricing details for using an endpoint"""

    specs: DataSpecs
    """Detailed specifications of a hardware configuration"""

    updated_at: datetime
    """Timestamp of when the hardware status was last updated"""

    availability: Optional[DataAvailability] = None
    """Indicates the current availability status of a hardware configuration"""


class HardwareListResponse(BaseModel):
    data: List[Data]

    object: Literal["list"]
