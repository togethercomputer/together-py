# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["ShapingJobStatus"]

ShapingJobStatus: TypeAlias = Literal[
    "pending", "queued", "running", "completed", "cancelled", "cancel_requested", "error", "user_error"
]
