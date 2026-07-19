# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

from ..._types import SequenceNotStr

__all__ = ["DeploymentPlacementConfigParam"]


class DeploymentPlacementConfigParam(TypedDict, total=False):
    """Inline placement parameters expanded into scheduling rules by the server."""

    constraint: Literal["ENFORCEMENT_REQUIRED", "ENFORCEMENT_PREFERRED"]
    """How strictly the regions list is enforced."""

    regions: SequenceNotStr[str]
    """Regions where the deployment is allowed to run.

    Multiple regions allow best-effort replica spreading.
    """
