# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel
from .whoami_user import WhoamiUser

__all__ = ["WhoamiUserJwt"]


class WhoamiUserJwt(BaseModel):
    type: Literal["user_jwt"]
    """Always `user_jwt`."""

    user: WhoamiUser
