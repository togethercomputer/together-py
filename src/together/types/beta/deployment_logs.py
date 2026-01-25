# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["DeploymentLogs"]


class DeploymentLogs(BaseModel):
    lines: Optional[List[str]] = None
