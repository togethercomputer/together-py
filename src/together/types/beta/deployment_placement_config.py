# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["DeploymentPlacementConfig"]


class DeploymentPlacementConfig(BaseModel):
    """Inline placement parameters expanded into scheduling rules by the server."""

    constraint: Optional[Literal["ENFORCEMENT_REQUIRED", "ENFORCEMENT_PREFERRED"]] = None
    """How strictly the regions list is enforced."""

    regions: Optional[List[str]] = None
    """Regions where the deployment is allowed to run.

    Multiple regions allow best-effort replica spreading.
    """
