# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = [
    "TrainingSessionCreateParams",
    "Body",
    "BodyLoraConfig",
    "BodyLrSchedulerConfig",
    "BodyLrSchedulerConfigLinear",
    "BodyLrSchedulerConfigLinearParams",
    "BodyOptimizerConfig",
    "BodyOptimizerConfigAdamw",
    "BodyOptimizerConfigAdamwParams",
]


class TrainingSessionCreateParams(TypedDict, total=False):
    body: Required[Body]


class BodyLoraConfig(TypedDict, total=False):
    """LoRA adapter configuration"""

    alpha: int
    """Alpha of the LoRA adapter"""

    dropout: float
    """Dropout of the LoRA adapter"""

    rank: int
    """Rank of the LoRA adapter"""


class BodyLrSchedulerConfigLinearParams(TypedDict, total=False):
    """Linear learning rate scheduler parameters"""

    lr_min: float
    """Minimum learning rate at the end of linear decay"""

    warmup_steps: int
    """Number of warmup steps"""


class BodyLrSchedulerConfigLinear(TypedDict, total=False):
    """Linear learning rate scheduler configuration"""

    params: BodyLrSchedulerConfigLinearParams
    """Linear learning rate scheduler parameters"""


class BodyLrSchedulerConfig(TypedDict, total=False):
    """Learning rate scheduler configuration"""

    linear: BodyLrSchedulerConfigLinear
    """Linear learning rate scheduler configuration"""


class BodyOptimizerConfigAdamwParams(TypedDict, total=False):
    """AdamW optimizer parameters"""

    beta1: float
    """First moment decay rate"""

    beta2: float
    """Second moment decay rate"""

    eps: float
    """Epsilon for numerical stability"""

    lr: float
    """Learning rate"""

    weight_decay: float
    """Weight decay coefficient"""


class BodyOptimizerConfigAdamw(TypedDict, total=False):
    """AdamW optimizer configuration"""

    params: BodyOptimizerConfigAdamwParams
    """AdamW optimizer parameters"""


class BodyOptimizerConfig(TypedDict, total=False):
    """Optimizer configuration. If omitted, defaults to AdamW with default parameters."""

    adamw: BodyOptimizerConfigAdamw
    """AdamW optimizer configuration"""

    max_grad_norm: float
    """Maximum gradient norm for gradient clipping. Applies to all optimizer types."""


class Body(TypedDict, total=False):
    base_model: Required[str]
    """Base model to use for the training session"""

    checkpoint_id: str
    """Checkpoint ID to use for the training session"""

    lora_config: BodyLoraConfig
    """LoRA adapter configuration"""

    lr_scheduler_config: BodyLrSchedulerConfig
    """Learning rate scheduler configuration"""

    optimizer_config: BodyOptimizerConfig
    """Optimizer configuration. If omitted, defaults to AdamW with default parameters."""
