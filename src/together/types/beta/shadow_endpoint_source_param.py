# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from ..._utils import PropertyInfo
from .shadow_uniform_sampling_param import ShadowUniformSamplingParam
from .shadow_key_based_sampling_param import ShadowKeyBasedSamplingParam
from .shadow_adaptive_uniform_sampling_param import ShadowAdaptiveUniformSamplingParam
from .shadow_adaptive_key_based_sampling_param import ShadowAdaptiveKeyBasedSamplingParam

__all__ = [
    "ShadowEndpointSourceParam",
    "Sampling",
    "SamplingUniform",
    "SamplingKeyBased",
    "SamplingAdaptiveUniform",
    "SamplingAdaptiveKeyBased",
]


class SamplingUniform(TypedDict, total=False):
    uniform: Required[ShadowUniformSamplingParam]
    """Fixed-rate random sampling of endpoint requests."""


class SamplingKeyBased(TypedDict, total=False):
    key_based: Required[Annotated[ShadowKeyBasedSamplingParam, PropertyInfo(alias="keyBased")]]
    """Fixed-rate sampling of distinct key values with sticky decisions."""


class SamplingAdaptiveUniform(TypedDict, total=False):
    adaptive_uniform: Required[Annotated[ShadowAdaptiveUniformSamplingParam, PropertyInfo(alias="adaptiveUniform")]]
    """Adaptive random sampling that throttles toward a target QPS."""


class SamplingAdaptiveKeyBased(TypedDict, total=False):
    adaptive_key_based: Required[Annotated[ShadowAdaptiveKeyBasedSamplingParam, PropertyInfo(alias="adaptiveKeyBased")]]
    """Adaptive sticky-key sampling that throttles toward a target QPS."""


Sampling: TypeAlias = Union[SamplingUniform, SamplingKeyBased, SamplingAdaptiveUniform, SamplingAdaptiveKeyBased]


class ShadowEndpointSourceParam(TypedDict, total=False):
    """Endpoint-level source that samples endpoint traffic at the API gateway."""

    sampling: Required[Sampling]
    """Sampling strategy for endpoint-level shadow traffic.

    Exactly one strategy must be set.
    """
