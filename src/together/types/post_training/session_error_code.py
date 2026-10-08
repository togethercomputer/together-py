# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["SessionErrorCode"]

SessionErrorCode: TypeAlias = Literal[
    "TRAINING_SESSION_ERROR_CODE_RESOURCE_UNAVAILABLE",
    "TRAINING_SESSION_ERROR_CODE_RESOURCE_AT_CAPACITY",
    "TRAINING_SESSION_ERROR_CODE_TIMED_OUT",
    "TRAINING_SESSION_ERROR_CODE_SESSION_FAILED",
]
