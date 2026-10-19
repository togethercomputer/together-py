# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel
from .whoami_user import WhoamiUser
from .whoami_organization import WhoamiOrganization

__all__ = ["WhoamiUserOrgJwt"]


class WhoamiUserOrgJwt(BaseModel):
    organization: WhoamiOrganization

    type: Literal["user_org_jwt"]
    """Always `user_org_jwt`."""

    user: WhoamiUser
