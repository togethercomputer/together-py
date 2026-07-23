from __future__ import annotations

from typing import Optional
from datetime import datetime

from ..._models import BaseModel


class TokenizedDatasetDownloadResponse(BaseModel):
    """Presigned download metadata for a fine-tune tokenized dataset archive."""

    url: str
    filename: str
    size: int
    content_type: Optional[str] = None
    expires_at: Optional[datetime] = None
