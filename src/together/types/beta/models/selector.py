# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["Selector"]


class Selector(BaseModel):
    """Hardware or runtime requirement expressed as a key-value pair."""

    key: str
    """Selector name, such as GPU type, GPU count, or optimization profile."""

    value: str
    """Required value for the selector."""
