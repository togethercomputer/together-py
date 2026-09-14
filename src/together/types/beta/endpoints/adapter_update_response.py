# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["AdapterUpdateResponse", "PerCluster"]


class PerCluster(BaseModel):
    """Controller-reported load state for an adapter on one deployment cluster."""

    adapter_model_id: str = FieldInfo(alias="adapterModelId")
    """Adapter model identifier for this status row."""

    cluster_id: str = FieldInfo(alias="clusterId")
    """Cluster reporting this adapter status."""

    failed_pod_count: int = FieldInfo(alias="failedPodCount")
    """Number of pods that failed to load the adapter."""

    ready_pod_count: int = FieldInfo(alias="readyPodCount")
    """Number of pods with the adapter ready to serve."""

    state: Literal[
        "ADAPTER_LOAD_STATE_PENDING",
        "ADAPTER_LOAD_STATE_LOADING",
        "ADAPTER_LOAD_STATE_READY",
        "ADAPTER_LOAD_STATE_REMOVING",
        "ADAPTER_LOAD_STATE_FAILED",
    ]
    """Current adapter load state in this cluster."""

    total_pod_count: int = FieldInfo(alias="totalPodCount")
    """Total pods expected to report adapter load state."""

    adapter_model: Optional[str] = FieldInfo(alias="adapterModel", default=None)
    """
    Resource name of the adapter model, using
    projects/{projectId}/models/{adapterModelId}.
    """

    loaded_at: Optional[datetime] = FieldInfo(alias="loadedAt", default=None)
    """Time when the adapter first reached READY in this cluster."""

    message: Optional[str] = None
    """Human-readable details about the current adapter state."""

    realized_etag: Optional[str] = FieldInfo(alias="realizedEtag", default=None)
    """Adapter row etag observed by the controller when it wrote this status."""

    realized_revision: Optional[str] = FieldInfo(alias="realizedRevision", default=None)
    """
    Resource name of the adapter model revision currently loaded in this cluster,
    using projects/{projectId}/models/{adapterModelId}/revisions/{revisionId}.
    """

    realized_revision_id: Optional[str] = FieldInfo(alias="realizedRevisionId", default=None)
    """Adapter revision currently loaded on pods in this cluster."""

    reason: Optional[str] = None
    """Stable reason code for the current adapter state."""

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)
    """Time when this adapter status was last updated."""


class AdapterUpdateResponse(BaseModel):
    """Adapter attached to a deployment with desired revision and observed load state."""

    adapter_model_id: str = FieldInfo(alias="adapterModelId")
    """Adapter model identifier attached to the deployment."""

    desired_revision_id: str = FieldInfo(alias="desiredRevisionId")
    """Adapter revision pinned on the deployment."""

    etag: str
    """Row-level etag required for UpdateAdapter and RemoveAdapter."""

    per_cluster: List[PerCluster] = FieldInfo(alias="perCluster")
    """Per-cluster adapter load state reported by the controller."""

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
