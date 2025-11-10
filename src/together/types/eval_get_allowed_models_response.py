# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["EvalGetAllowedModelsResponse"]


class EvalGetAllowedModelsResponse(BaseModel):
    x_model_list: Optional[List[str]] = FieldInfo(alias="model_list", default=None)
