# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import builtins
from typing import Optional

from .._models import BaseModel

__all__ = ["FineTuneDownloadResponse"]


class FineTuneDownloadResponse(BaseModel):
    id: Optional[str] = None

    checkpoint_step: Optional[int] = None

    filename: Optional[str] = None

    object: Optional[builtins.object] = None

    size: Optional[int] = None
