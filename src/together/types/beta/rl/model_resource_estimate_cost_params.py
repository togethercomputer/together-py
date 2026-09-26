# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .optimizer_config_param import OptimizerConfigParam

__all__ = ["ModelResourceEstimateCostParams", "ComputeConfig"]


class ModelResourceEstimateCostParams(TypedDict, total=False):
    base_model: Required[str]
    """Base model to provision the resource for, selected from /rl/supported-models"""

    compute_config: ComputeConfig
    """Compute layout to provision."""

    lora_enabled: bool
    """Whether the resource hosts LoRA sessions or a single full-weight session"""

    optimizer_config: OptimizerConfigParam
    """Optimizer configuration for this resource."""


class ComputeConfig(TypedDict, total=False):
    """Compute layout to provision."""

    gpu_type: Literal["H100-80GB", "B200-SXM"]
    """GPU type to provision. Omit to use the model's default GPU type."""

    num_generator_replicas: int
    """Number of generator replicas. 0 runs the trainer only, with no generator."""
