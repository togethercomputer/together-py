# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel
from .whoami_api_key import WhoamiAPIKey
from .whoami_project import WhoamiProject
from .whoami_organization import WhoamiOrganization

__all__ = ["WhoamiProjectAPIKey"]


class WhoamiProjectAPIKey(BaseModel):
    api_key: WhoamiAPIKey

    organization: WhoamiOrganization

    project: WhoamiProject

    type: Literal["project_api_key"]
    """Always `project_api_key`."""
