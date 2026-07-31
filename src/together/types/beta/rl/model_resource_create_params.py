# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .optimizer_config_param_param import OptimizerConfigParam

__all__ = ["ModelResourceCreateParams", "ComputeConfig"]


class ModelResourceCreateParams(TypedDict, total=False):
    base_model: Required[str]
    """Base model to provision the resource for"""

    compute_config: ComputeConfig
    """Compute layout to provision."""

    lora_enabled: bool
    """Whether the resource hosts LoRA sessions or a single full-weight session"""

    optimizer_config: OptimizerConfigParam
    """Optimizer configuration for this resource."""


class ComputeConfig(TypedDict, total=False):
    """Compute layout to provision."""

    num_generator_replicas: int
    """Number of generator replicas. 0 runs the trainer only, with no generator."""
