# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["RollingConfig"]


class RollingConfig(BaseModel):
    """Rolling strategy configuration.

    The target ramps up one replica per rung while the source shrinks to what its remaining traffic share needs.
    """

    pass
