# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .supported_model_deployment_profile import SupportedModelDeploymentProfile

__all__ = ["SupportedModel"]


class SupportedModel(BaseModel):
    """Curated catalog entry for a platform-supported model."""

    id: str
    """Unique ID of the deployable Together-hosted base model."""

    base_model: str = FieldInfo(alias="baseModel")
    """
    Resource name for the base model as `projects/{projectId}/models/{modelId}`;
    empty when unresolved.
    """

    base_model_id: str = FieldInfo(alias="baseModelId")
    """
    Bare model ID for the architecture's base model; empty when no base model is
    linked.
    """

    capabilities: List[
        Literal[
            "CAPABILITY_CHAT",
            "CAPABILITY_EMBEDDING",
            "CAPABILITY_RERANKING",
            "CAPABILITY_IMAGE_GENERATION",
            "CAPABILITY_VIDEO_GENERATION",
        ]
    ]
    """High-level tasks the model supports."""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Timestamp when the catalog entry was created."""

    deployment_profiles: List[SupportedModelDeploymentProfile] = FieldInfo(alias="deploymentProfiles")
    """Certified deployment profiles available for the model."""

    display_name: str = FieldInfo(alias="displayName")
    """Catalog-controlled human-readable model name."""

    display_type: str = FieldInfo(alias="displayType")
    """
    UI-facing model type badge, such as chat, language, code, image, embedding,
    rerank, moderation, audio, video, or transcribe.
    """

    input_modalities: List[Literal["MODALITY_TEXT", "MODALITY_IMAGE", "MODALITY_AUDIO", "MODALITY_VIDEO"]] = FieldInfo(
        alias="inputModalities"
    )
    """Input modalities supported by the model."""

    name: str
    """Catalog-controlled HF model ID used for inference."""

    output_modalities: List[Literal["MODALITY_TEXT", "MODALITY_IMAGE", "MODALITY_AUDIO", "MODALITY_VIDEO"]] = FieldInfo(
        alias="outputModalities"
    )
    """Output modalities produced by the model."""

    products: List[Literal["PRODUCT_SERVERLESS", "PRODUCT_DEDICATED", "PRODUCT_FINE_TUNING"]]
    """Product surfaces where the model is offered."""

    publisher: str
    """Organization or publisher associated with the model."""

    status: Literal[
        "SUPPORTED_MODEL_STATUS_RECOMMENDED",
        "SUPPORTED_MODEL_STATUS_SUPPORTED",
        "SUPPORTED_MODEL_STATUS_DEPRECATED",
        "SUPPORTED_MODEL_STATUS_HIDDEN",
    ]
    """Catalog recommendation status for the model."""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Timestamp when the catalog entry was last updated."""

    architecture: Optional[str] = None
    """Model architecture from the underlying weights metadata."""

    context_length: Optional[str] = FieldInfo(alias="contextLength", default=None)
    """Maximum context length from the underlying weights metadata."""

    description: Optional[str] = None
    """Human-readable model description."""

    family_id: Optional[str] = FieldInfo(alias="familyId", default=None)
    """Model family identifier for related catalog entries."""

    features: Optional[List[Literal["FEATURE_TOOL_CALLING", "FEATURE_STRUCTURED_OUTPUT", "FEATURE_REASONING"]]] = None
    """Advanced features exposed by the model."""

    input_format: Optional[str] = FieldInfo(alias="inputFormat", default=None)
    """Preferred input format for the model."""

    output_format: Optional[str] = FieldInfo(alias="outputFormat", default=None)
    """Preferred output format for the model."""

    serverless_endpoint: Optional[str] = FieldInfo(alias="serverlessEndpoint", default=None)
    """Serverless endpoint name for inference, if available."""

    tags: Optional[List[str]] = None
    """Searchable catalog tags for the model."""
