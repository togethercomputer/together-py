# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .shadow_uniform_sampling_response import ShadowUniformSamplingResponse
from .shadow_key_based_sampling_response import ShadowKeyBasedSamplingResponse
from .shadow_adaptive_uniform_sampling_response import ShadowAdaptiveUniformSamplingResponse
from .shadow_adaptive_key_based_sampling_response import ShadowAdaptiveKeyBasedSamplingResponse

__all__ = [
    "ShadowEndpointSourceResponse",
    "Sampling",
    "SamplingUniform",
    "SamplingKeyBased",
    "SamplingAdaptiveUniform",
    "SamplingAdaptiveKeyBased",
]


class SamplingUniform(BaseModel):
    uniform: ShadowUniformSamplingResponse
    """Fixed-rate random sampling returned by the API.

    A zero rate may be omitted by JSON serialization.
    """


class SamplingKeyBased(BaseModel):
    key_based: ShadowKeyBasedSamplingResponse = FieldInfo(alias="keyBased")
    """Fixed-rate sticky-key sampling returned by the API.

    A zero rate may be omitted by JSON serialization.
    """


class SamplingAdaptiveUniform(BaseModel):
    adaptive_uniform: ShadowAdaptiveUniformSamplingResponse = FieldInfo(alias="adaptiveUniform")
    """Adaptive random sampling returned by the API."""


class SamplingAdaptiveKeyBased(BaseModel):
    adaptive_key_based: ShadowAdaptiveKeyBasedSamplingResponse = FieldInfo(alias="adaptiveKeyBased")
    """Adaptive sticky-key sampling returned by the API."""


Sampling: TypeAlias = Union[SamplingUniform, SamplingKeyBased, SamplingAdaptiveUniform, SamplingAdaptiveKeyBased]


class ShadowEndpointSourceResponse(BaseModel):
    """Endpoint-level source returned for a shadow experiment."""

    sampling: Sampling
    """Sampling strategy returned for endpoint-level shadow traffic."""
