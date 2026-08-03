# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .supported_model_performance_benchmarks import SupportedModelPerformanceBenchmarks

__all__ = ["SupportedModelDeploymentProfile"]


class SupportedModelDeploymentProfile(BaseModel):
    """Certified deployment profile for a supported model."""

    certified_config_revision_id: str = FieldInfo(alias="certifiedConfigRevisionId")
    """Certified configuration revision identifier."""

    certified_model_revision_id: str = FieldInfo(alias="certifiedModelRevisionId")
    """Certified model weight revision identifier, if available."""

    config: str
    """
    Certified config revision in the form
    `projects/{projectId}/configs/{configRevisionId}`. Omitted when the profile does
    not pin a config.
    """

    gpu_count: int = FieldInfo(alias="gpuCount")
    """Number of GPUs required by the profile."""

    gpu_type: str = FieldInfo(alias="gpuType")
    """GPU instance type for the profile."""

    model: str
    """
    Deployable model resource in the form
    `projects/{projectId}/models/{modelId}[/revisions/{revisionId}]`. Omitted when
    the profile does not pin model weights.
    """

    api_model_name: str = FieldInfo(alias="modelName")
    """
    Fully-qualified deploy model name in the form `{projectSlug}/{modelName}`, such
    as `Qwen/Qwen3.5-9B-FP8`; empty when no public model is linked.
    """

    parallelism: str
    """
    Free-form parallelism spec for the profile, such as TP8, TP4, EP, or PD;
    supersedes tensor_parallel_size.
    """

    performance_benchmarks: SupportedModelPerformanceBenchmarks = FieldInfo(alias="performanceBenchmarks")
    """Performance benchmarks for the profile, if available."""

    profile_id: str = FieldInfo(alias="profileId")
    """Stable profile identifier, usually the certified config id."""

    quantization: str
    """Quantization method for the profile, if available."""

    tensor_parallel_size: Optional[int] = FieldInfo(alias="tensorParallelSize", default=None)
    """Deprecated.

    Use `parallelism`. Legacy tensor-parallel shard count for the profile.
    """
