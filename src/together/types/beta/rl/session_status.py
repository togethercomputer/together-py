# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["SessionStatus"]

SessionStatus: TypeAlias = Literal[
    "TRAINING_SESSION_STATUS_UNSPECIFIED",
    "TRAINING_SESSION_STATUS_CREATING",
    "TRAINING_SESSION_STATUS_RUNNING",
    "TRAINING_SESSION_STATUS_STOPPED",
    "TRAINING_SESSION_STATUS_STOPPING",
    "TRAINING_SESSION_STATUS_ERROR",
    "TRAINING_SESSION_STATUS_EXPIRED",
]
