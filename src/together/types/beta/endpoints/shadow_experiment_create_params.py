# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from ..shadow_source_param import ShadowSourceParam

__all__ = ["ShadowExperimentCreateParams", "Target"]


class ShadowExperimentCreateParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    name: Required[str]
    """Human-readable shadow experiment name, unique within the endpoint.

    At most 256 characters.
    """

    source: Required[ShadowSourceParam]
    """Traffic source for a shadow experiment.

    The public API supports endpoint sources only.
    """

    targets: Iterable[Target]
    """Optional initial target deployments.

    At most 100 targets; manage later changes through the target APIs.
    """


class Target(TypedDict, total=False):
    """
    Deployment under the parent endpoint that should receive mirrored requests from a shadow experiment.
    """

    name: Required[str]
    """Human-readable target name, unique within the shadow experiment.

    At most 256 characters.
    """

    target_deployment_id: Required[Annotated[str, PropertyInfo(alias="targetDeploymentId")]]
    """Deployment under the parent endpoint that receives mirrored traffic.

    It must not be a live traffic-split member or the source or target of an active
    rollout; traffic-split weight 0 warm-up targets are allowed.
    """

    description: str
    """Optional free-form target description."""
