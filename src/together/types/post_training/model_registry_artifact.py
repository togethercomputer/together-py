# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["ModelRegistryArtifact"]


class ModelRegistryArtifact(BaseModel):
    """A specific revision of a model in the Together model registry"""

    id: str
    """ID of the model in the Together model registry, as used by the models API"""

    revision_id: str
    """Revision of the model that holds this checkpoint"""
