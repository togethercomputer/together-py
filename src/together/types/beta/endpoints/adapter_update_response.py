# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .deployment_adapter_status import DeploymentAdapterStatus

__all__ = ["AdapterUpdateResponse"]


class AdapterUpdateResponse(BaseModel):
    """Adapter attached to a deployment with desired revision and observed load state."""

    adapter_model_id: str = FieldInfo(alias="adapterModelId")
    """Adapter model identifier attached to the deployment."""

    desired_revision_id: str = FieldInfo(alias="desiredRevisionId")
    """Adapter revision pinned on the deployment."""

    etag: str
    """Row-level etag required for UpdateAdapter and RemoveAdapter."""

    per_cluster: List[DeploymentAdapterStatus] = FieldInfo(alias="perCluster")
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
