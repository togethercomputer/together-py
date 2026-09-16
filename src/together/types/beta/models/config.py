# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .selector import Selector
from ...._models import BaseModel
from .certification import Certification

__all__ = ["Config"]


class Config(BaseModel):
    """
    Immutable, user-facing configuration revision that defines how a compatible model runs, including engine and hardware selectors.
    """

    id: str
    """Config revision identifier."""

    certifications: List[Certification]
    """Model, hardware, and runtime combinations certified for this config revision."""

    project_id: str = FieldInfo(alias="projectId")
    """ID of the project that owns the config revision.

    Public configs may be owned by a different project than the deployment.
    """

    reference_model: str = FieldInfo(alias="referenceModel")
    """
    Resource name of the referenced model, using
    `projects/{modelProject}/models/{modelId}`.
    """

    reference_model_id: str = FieldInfo(alias="referenceModelId")
    """Deprecated. Use `referenceModel`. Reference model identifier."""

    selectors: List[Selector]
    """Hardware and runtime selectors used to place and configure replicas."""

    draft_model: Optional[str] = FieldInfo(alias="draftModel", default=None)
    """
    Resource name of the draft model, using
    `projects/{draftProject}/models/{modelId}`; empty when speculative decoding is
    not enabled.
    """
