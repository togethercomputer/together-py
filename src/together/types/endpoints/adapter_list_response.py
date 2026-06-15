# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["AdapterListResponse", "Data"]


class Data(BaseModel):
    adapter_name: Optional[str] = None

    endpoint_name: Optional[str] = None

    api_model_id: Optional[str] = FieldInfo(alias="model_id", default=None)
    """Combined endpoint:adapter identifier"""


class AdapterListResponse(BaseModel):
    data: Optional[List[Data]] = None

    object: Optional[str] = None
