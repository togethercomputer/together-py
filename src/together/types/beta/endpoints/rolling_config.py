# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["RollingConfig"]


class RollingConfig(BaseModel):
    """
    Rolling strategy configuration for small batches that ramp target replicas up while shrinking source replicas to what their remaining traffic share needs.
    """

    pass
