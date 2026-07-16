# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .shadow_experiments.shadow_experiment_target import ShadowExperimentTarget

__all__ = [
    "ShadowExperiment",
    "Source",
    "SourceEndpoint",
    "SourceEndpointSampling",
    "SourceEndpointSamplingUniform",
    "SourceEndpointSamplingUniformUniform",
    "SourceEndpointSamplingKeyBased",
    "SourceEndpointSamplingKeyBasedKeyBased",
    "SourceEndpointSamplingAdaptiveUniform",
    "SourceEndpointSamplingAdaptiveUniformAdaptiveUniform",
    "SourceEndpointSamplingAdaptiveKeyBased",
    "SourceEndpointSamplingAdaptiveKeyBasedAdaptiveKeyBased",
]


class SourceEndpointSamplingUniformUniform(BaseModel):
    """Fixed-rate random sampling returned by the API.

    A zero rate may be omitted by JSON serialization.
    """

    rate: Optional[float] = None
    """Fraction of requests sampled, from 0.0 to 1.0."""


class SourceEndpointSamplingUniform(BaseModel):
    uniform: SourceEndpointSamplingUniformUniform
    """Fixed-rate random sampling returned by the API.

    A zero rate may be omitted by JSON serialization.
    """


class SourceEndpointSamplingKeyBasedKeyBased(BaseModel):
    """Fixed-rate sticky-key sampling returned by the API.

    A zero rate may be omitted by JSON serialization.
    """

    key: str
    """Request-body field used as the sticky sampling key."""

    rate: Optional[float] = None
    """Fraction of distinct key values sampled, from 0.0 to 1.0."""


class SourceEndpointSamplingKeyBased(BaseModel):
    key_based: SourceEndpointSamplingKeyBasedKeyBased = FieldInfo(alias="keyBased")
    """Fixed-rate sticky-key sampling returned by the API.

    A zero rate may be omitted by JSON serialization.
    """


class SourceEndpointSamplingAdaptiveUniformAdaptiveUniform(BaseModel):
    """Adaptive random sampling returned by the API."""

    target_qps: float = FieldInfo(alias="targetQps")
    """Per-gateway-replica target QPS."""

    window: Optional[str] = None
    """Sliding window for QPS observation when explicitly configured."""


class SourceEndpointSamplingAdaptiveUniform(BaseModel):
    adaptive_uniform: SourceEndpointSamplingAdaptiveUniformAdaptiveUniform = FieldInfo(alias="adaptiveUniform")
    """Adaptive random sampling returned by the API."""


class SourceEndpointSamplingAdaptiveKeyBasedAdaptiveKeyBased(BaseModel):
    """Adaptive sticky-key sampling returned by the API."""

    key: str
    """Request-body field used as the sticky sampling key."""

    target_qps: float = FieldInfo(alias="targetQps")
    """Per-gateway-replica target QPS."""

    window: Optional[str] = None
    """Sliding window for QPS observation when explicitly configured."""


class SourceEndpointSamplingAdaptiveKeyBased(BaseModel):
    adaptive_key_based: SourceEndpointSamplingAdaptiveKeyBasedAdaptiveKeyBased = FieldInfo(alias="adaptiveKeyBased")
    """Adaptive sticky-key sampling returned by the API."""


SourceEndpointSampling: TypeAlias = Union[
    SourceEndpointSamplingUniform,
    SourceEndpointSamplingKeyBased,
    SourceEndpointSamplingAdaptiveUniform,
    SourceEndpointSamplingAdaptiveKeyBased,
]


class SourceEndpoint(BaseModel):
    """Endpoint-level source returned for a shadow experiment."""

    sampling: SourceEndpointSampling
    """Sampling strategy returned for endpoint-level shadow traffic."""


class Source(BaseModel):
    """Endpoint traffic source returned for a shadow experiment."""

    endpoint: SourceEndpoint
    """Endpoint-level source returned for a shadow experiment."""


class ShadowExperiment(BaseModel):
    """
    Experiment that mirrors sampled endpoint requests to target deployments without changing client responses.
    """

    id: str
    """Output only. Unique shadow experiment identifier."""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Timestamp when the experiment was created."""

    created_by: str = FieldInfo(alias="createdBy")
    """Identifier of the principal that created the experiment."""

    endpoint_id: str = FieldInfo(alias="endpointId")
    """Output only. Endpoint whose traffic this experiment samples."""

    etag: str
    """Opaque version tag for optimistic concurrency control.

    Returned on read; set it on update or delete requests for consistent
    read-modify-write.
    """

    name: str
    """Human-readable shadow experiment name, unique within the endpoint.

    At most 256 characters.
    """

    project_id: str = FieldInfo(alias="projectId")
    """Output only. Project that owns the parent endpoint."""

    source: Source
    """Endpoint traffic source returned for a shadow experiment."""

    state: Literal["SHADOW_EXPERIMENT_STATE_ACTIVE", "SHADOW_EXPERIMENT_STATE_INACTIVE"]
    """Derived serving state, active when the experiment has at least one target."""

    targets: List[ShadowExperimentTarget]
    """Target deployments that receive mirrored traffic."""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Timestamp when the experiment was last updated."""

    description: Optional[str] = None
    """User defined description."""
