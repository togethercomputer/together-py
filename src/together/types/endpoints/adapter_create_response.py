# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .deployment_adapter_status import DeploymentAdapterStatus

__all__ = ["AdapterCreateResponse"]


class AdapterCreateResponse(BaseModel):
    """Adapter attached to a deployment with desired revision and observed load state."""

    id: str
    """
    Adapter attachment `dad_` id used by get, update, and remove; stale ids never
    address a replacement after remove and re-add.
    """

    adapter_model_id: str = FieldInfo(alias="adapterModelId")
    """Adapter model identifier attached to the deployment."""

    desired_revision_id: str = FieldInfo(alias="desiredRevisionId")
    """Adapter revision pinned on the deployment."""

    etag: str
    """Row-level etag required for UpdateAdapter and RemoveAdapter."""

    per_cluster: List[DeploymentAdapterStatus] = FieldInfo(alias="perCluster")
    """
    Per-cluster adapter load state reported by the controller for the clusters the
    deployment is placed on. Empty while the deployment is stopped or being torn
    down, and briefly after AddAdapter.
    """

    serving_state: Literal[
        "ADAPTER_SERVING_STATE_INACTIVE",
        "ADAPTER_SERVING_STATE_LOADING",
        "ADAPTER_SERVING_STATE_READY",
        "ADAPTER_SERVING_STATE_FAILED",
    ] = FieldInfo(alias="servingState")
    """Whether the adapter can serve requests right now.

    INACTIVE means the deployment is stopped, scaled to zero, or being torn down;
    LOADING means a placed cluster has not finished loading it; READY means every
    placed cluster serves it; FAILED means a placed cluster failed to load it.
    """

    adapter_model: Optional[str] = FieldInfo(alias="adapterModel", default=None)
    """
    Resource name of the adapter model, using
    projects/{projectId}/models/{adapterModelId}.
    """

    desired_revision: Optional[str] = FieldInfo(alias="desiredRevision", default=None)
    """
    Resource name of the adapter model revision pinned on the deployment, using
    projects/{projectId}/models/{adapterModelId}/revisions/{revisionId}.
    """
