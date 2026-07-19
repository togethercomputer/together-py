# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["Config", "Certification", "Selector"]


class Certification(BaseModel):
    """Certification result for a model, config, and optional draft-model combination."""

    certification_type: Literal["CERTIFICATION_TYPE_CERTIFIED", "CERTIFICATION_TYPE_UNCERTIFIED"] = FieldInfo(
        alias="certificationType"
    )
    """Whether the model and config combination passed certification."""

    certified_at: datetime = FieldInfo(alias="certifiedAt")
    """Time when the certification decision was recorded."""

    certified_by: str = FieldInfo(alias="certifiedBy")
    """Service or reviewer that recorded the certification."""

    model: str
    """Resource name of the certified model."""

    api_model_revision_id: str = FieldInfo(alias="modelRevisionId")
    """Revision identifier of the certified model."""

    target: Literal["CERTIFICATION_TARGET_DE_SERVERLESS", "CERTIFICATION_TARGET_MRE"]
    """Product or serving environment for which the combination was evaluated."""

    draft_model: Optional[str] = FieldInfo(alias="draftModel", default=None)
    """Resource name of the certified draft model."""

    draft_model_revision_id: Optional[str] = FieldInfo(alias="draftModelRevisionId", default=None)
    """Revision identifier of the certified draft model."""

    notes: Optional[str] = None
    """Human-readable certification notes or limitations."""


class Selector(BaseModel):
    """Hardware or runtime requirement expressed as a key-value pair."""

    key: str
    """Selector name, such as GPU type, GPU count, or optimization profile."""

    value: str
    """Required value for the selector."""


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
