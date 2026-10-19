# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel
from .whoami_user import WhoamiUser
from .whoami_project import WhoamiProject
from .whoami_organization import WhoamiOrganization

__all__ = ["WhoamiUserOrgProjectJwt"]


class WhoamiUserOrgProjectJwt(BaseModel):
    organization: WhoamiOrganization

    project: WhoamiProject

    type: Literal["user_org_project_jwt"]
    """Always `user_org_project_jwt`."""

    user: WhoamiUser
