# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["WeightSyncType"]

WeightSyncType: TypeAlias = Literal[
    "WEIGHT_SYNC_TYPE_SYNCHRONOUS", "WEIGHT_SYNC_TYPE_BACKGROUND_PUBLISH", "WEIGHT_SYNC_TYPE_PIPELINE"
]
