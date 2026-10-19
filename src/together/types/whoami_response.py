# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from .._utils import PropertyInfo
from .whoami_user_jwt import WhoamiUserJwt
from .whoami_org_api_key import WhoamiOrgAPIKey
from .whoami_user_org_jwt import WhoamiUserOrgJwt
from .whoami_project_api_key import WhoamiProjectAPIKey
from .whoami_user_org_project_jwt import WhoamiUserOrgProjectJwt

__all__ = ["WhoamiResponse"]

WhoamiResponse: TypeAlias = Annotated[
    Union[WhoamiProjectAPIKey, WhoamiOrgAPIKey, WhoamiUserJwt, WhoamiUserOrgJwt, WhoamiUserOrgProjectJwt],
    PropertyInfo(discriminator="type"),
]
