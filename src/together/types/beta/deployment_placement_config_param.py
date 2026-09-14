# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._types import SequenceNotStr
from ..._utils import PropertyInfo

__all__ = ["DeploymentPlacementConfigParam", "CompliancePolicy"]


class CompliancePolicy(TypedDict, total=False):
    """Compliance regimes required by a deployment placement policy."""

    hipaa: bool
    """Restrict placement to HIPAA-attested clusters."""


class DeploymentPlacementConfigParam(TypedDict, total=False):
    """Inline placement parameters expanded into scheduling rules by the server."""

    compliance_policy: Annotated[CompliancePolicy, PropertyInfo(alias="compliancePolicy")]
    """Compliance regimes required by a deployment placement policy."""

    constraint: Literal["ENFORCEMENT_REQUIRED", "ENFORCEMENT_PREFERRED"]
    """How strictly the regions list is enforced."""

    regions: SequenceNotStr[str]
    """Regions where the deployment is allowed to run.

    Multiple regions allow best-effort replica spreading.
    """
