# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel
from .file_response import FileResponse

__all__ = ["FileList"]


class FileList(BaseModel):
    data: List[FileResponse]
