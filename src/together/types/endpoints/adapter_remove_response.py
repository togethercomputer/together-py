# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["AdapterRemoveResponse"]


class AdapterRemoveResponse(BaseModel):
    deleted: Optional[bool] = None

    api_model_id: Optional[str] = FieldInfo(alias="model_id", default=None)
