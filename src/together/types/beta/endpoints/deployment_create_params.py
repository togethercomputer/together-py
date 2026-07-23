# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from ...._utils import PropertyInfo
from ..deployment_autoscaling_param import DeploymentAutoscalingParam
from ..deployment_placement_config_param import DeploymentPlacementConfigParam

__all__ = ["DeploymentCreateParams", "Placement", "PlacementInline", "PlacementProfile"]


class DeploymentCreateParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """ID of the project that owns the endpoint."""

    autoscaling: Required[DeploymentAutoscalingParam]
    """Autoscaling configuration for a deployment."""

    name: Required[str]
    """Name for the deployment within its endpoint.

    Returned as a fully-qualified endpoint string.
    """

    validate_only: Annotated[bool, PropertyInfo(alias="validateOnly")]
    """When true, validates the request without creating or provisioning a deployment."""

    config: str
    """
    Immutable config revision in the form
    `projects/{projectId}/configs/{configRevisionId}`. The config must be compatible
    with the model.
    """

    config_id: Annotated[str, PropertyInfo(alias="configId")]
    """Deprecated.

    Use `config`. Config revision identifier to deploy, accepted when `config` is
    unset.
    """

    enable_lora: Annotated[bool, PropertyInfo(alias="enableLora")]
    """Enables dynamic loading of LoRA adapters on the deployment."""

    model: str
    """
    Model resource name in the form
    `projects/{projectId}/models/{modelId}[/revisions/{revisionId}]`. Omit the
    revision segment to pin the latest revision at creation time.
    """

    model_id: Annotated[str, PropertyInfo(alias="modelId")]
    """Deprecated.

    Use `model`. Model identifier to serve, accepted when `model` is unset.
    """

    model_revision_id: Annotated[str, PropertyInfo(alias="modelRevisionId")]
    """Deprecated.

    Use `model` with a /revisions/{revisionId} segment. If omitted, the latest
    revision is resolved at creation.
    """

    placement: Placement
    """Placement controls where a deployment is scheduled."""


class PlacementInline(TypedDict, total=False):
    inline: Required[DeploymentPlacementConfigParam]
    """Inline placement parameters expanded into scheduling rules by the server."""


class PlacementProfile(TypedDict, total=False):
    profile: Required[str]
    """UID of a saved placement profile."""


Placement: TypeAlias = Union[PlacementInline, PlacementProfile]
