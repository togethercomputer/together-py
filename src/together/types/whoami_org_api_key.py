# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel
from .whoami_api_key import WhoamiAPIKey
from .whoami_organization import WhoamiOrganization

__all__ = ["WhoamiOrgAPIKey"]


class WhoamiOrgAPIKey(BaseModel):
    api_key: WhoamiAPIKey

    organization: WhoamiOrganization

    type: Literal["org_api_key"]
    """Always `org_api_key`."""
