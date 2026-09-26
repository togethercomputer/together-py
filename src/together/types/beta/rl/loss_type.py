# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["LossType"]

LossType: TypeAlias = Literal[
    "LOSS_TYPE_UNSPECIFIED",
    "LOSS_TYPE_CROSS_ENTROPY",
    "LOSS_TYPE_GRPO",
    "LOSS_TYPE_IMPORTANCE_SAMPLING",
    "LOSS_TYPE_PPO",
    "LOSS_TYPE_CISPO",
    "LOSS_TYPE_DRO",
    "LOSS_TYPE_DPPO",
]
