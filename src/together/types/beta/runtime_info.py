# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["RuntimeInfo"]


class RuntimeInfo(BaseModel):
    """Runtime information derived from the deployment's configuration."""

    engine_type: Optional[str] = FieldInfo(alias="engineType", default=None)
    """Serving engine, such as `vllm`, `trtllm`, or `sglang`."""

    engine_version: Optional[str] = FieldInfo(alias="engineVersion", default=None)
    """Version of the serving engine."""

    function_calling_supported: Optional[bool] = FieldInfo(alias="functionCallingSupported", default=None)
    """Whether the runtime accepts tool and function-calling requests."""

    structured_output_supported: Optional[bool] = FieldInfo(alias="structuredOutputSupported", default=None)
    """Whether the runtime can constrain generation to a structured output schema."""
