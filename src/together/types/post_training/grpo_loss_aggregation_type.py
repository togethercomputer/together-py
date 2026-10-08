# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["GrpoLossAggregationType"]

GrpoLossAggregationType: TypeAlias = Literal[
    "GRPO_LOSS_AGGREGATION_TYPE_UNSPECIFIED",
    "GRPO_LOSS_AGGREGATION_TYPE_FIXED_HORIZON",
    "GRPO_LOSS_AGGREGATION_TYPE_TOKEN_MEAN",
    "GRPO_LOSS_AGGREGATION_TYPE_SEQUENCE_MEAN",
]
