# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["FileListResponse", "FileListResponseItem", "FileListResponseItemPricing"]


class FileListResponseItemPricing(BaseModel):
    base: Optional[float] = None

    finetune: Optional[float] = None

    hourly: Optional[float] = None

    input: Optional[float] = None

    output: Optional[float] = None


class FileListResponseItem(BaseModel):
    id: Optional[str] = None

    context_length: Optional[int] = None

    created: Optional[int] = None

    display_name: Optional[str] = None

    license: Optional[str] = None

    link: Optional[str] = None

    object: Optional[str] = None

    organization: Optional[str] = None

    pricing: Optional[FileListResponseItemPricing] = None

    type: Optional[str] = None


FileListResponse = List[FileListResponseItem]
