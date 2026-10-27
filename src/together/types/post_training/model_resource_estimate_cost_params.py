# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .optimizer_config_param import OptimizerConfigParam

__all__ = ["ModelResourceEstimateCostParams", "ComputeConfig"]


class ModelResourceEstimateCostParams(TypedDict, total=False):
    base_model: Required[str]
    """Base model to provision the resource for, selected from /rl/supported-models"""

    base_weights_ref: str
    """
    Model in this project's model registry whose weights the resource trains in
    place of the base model's own. It must be a full-weight model.
    """

    compute_config: ComputeConfig
    """Compute layout to provision."""

    inactive_timeout: int
    """
    Minutes without activity after which the resource stops and its sessions expire,
    counted from when it becomes ready and from its last activity. Every operation
    on any of its sessions restarts the count, and an extend expiry call can keep it
    up longer.
    """

    lora_enabled: bool
    """Whether the resource hosts LoRA sessions or a single full-weight session"""

    optimizer_config: OptimizerConfigParam
    """Optimizer configuration for this resource."""


class ComputeConfig(TypedDict, total=False):
    """Compute layout to provision."""

    gpu_type: Literal["B200-SXM"]
    """GPU type to provision. Omit to use the model's default GPU type."""

    num_generator_replicas: int
    """Number of generator replicas. 0 runs the trainer only, with no generator."""
