"""`GET /v3/whoami` for the CLI. The SDK's `client.whoami()` still calls `/v1/whoami`."""

from __future__ import annotations

from typing import Any, Union, cast
from typing_extensions import Literal, Annotated, TypeAlias

import httpx

from together import AsyncTogether
from together._utils import PropertyInfo
from together._models import BaseModel

__all__ = [
    "WhoamiApiKey",
    "WhoamiOrganization",
    "WhoamiProject",
    "WhoamiUser",
    "WhoamiProjectApiKey",
    "WhoamiOrgApiKey",
    "WhoamiUserJwt",
    "WhoamiUserOrgJwt",
    "WhoamiUserOrgProjectJwt",
    "WhoamiResponse",
    "whoami_url",
    "fetch_whoami",
    "project_of",
    "organization_of",
]


class WhoamiApiKey(BaseModel):
    id: str


class WhoamiOrganization(BaseModel):
    id: str

    name: str


class WhoamiProject(BaseModel):
    id: str

    name: str

    slug: str


class WhoamiUser(BaseModel):
    id: str


class WhoamiProjectApiKey(BaseModel):
    type: Literal["project_api_key"]

    api_key: WhoamiApiKey

    organization: WhoamiOrganization

    project: WhoamiProject


class WhoamiOrgApiKey(BaseModel):
    type: Literal["org_api_key"]

    api_key: WhoamiApiKey

    organization: WhoamiOrganization


class WhoamiUserJwt(BaseModel):
    type: Literal["user_jwt"]

    user: WhoamiUser


class WhoamiUserOrgJwt(BaseModel):
    type: Literal["user_org_jwt"]

    user: WhoamiUser

    organization: WhoamiOrganization


class WhoamiUserOrgProjectJwt(BaseModel):
    type: Literal["user_org_project_jwt"]

    user: WhoamiUser

    organization: WhoamiOrganization

    project: WhoamiProject


# `type` selects the variant and which of user / api_key / organization / project are present.
WhoamiResponse: TypeAlias = Annotated[
    Union[
        WhoamiProjectApiKey,
        WhoamiOrgApiKey,
        WhoamiUserJwt,
        WhoamiUserOrgJwt,
        WhoamiUserOrgProjectJwt,
    ],
    PropertyInfo(discriminator="type"),
]


def whoami_url(base_url: httpx.URL) -> str:
    """`/v3/whoami` on the client's host: the base URL with its trailing `/v1` replaced by `/v3`."""
    path = base_url.path.rstrip("/")
    if path.endswith("/v1"):
        path = path[: -len("/v1")]
    return str(base_url.copy_with(path=f"{path}/v3/whoami", query=None, fragment=None))


async def fetch_whoami(client: AsyncTogether) -> WhoamiResponse:
    """Identity of the client's credentials (API key or `tg login` token) from `/v3/whoami`."""
    # `WhoamiResponse` is an annotated union, which is what the response parser needs and
    # not a class `cast_to` is typed as.
    return cast(
        WhoamiResponse,
        await client.get(whoami_url(client.base_url), cast_to=cast(Any, WhoamiResponse)),
    )


def project_of(identity: WhoamiResponse) -> WhoamiProject | None:
    project = getattr(identity, "project", None)
    if isinstance(project, WhoamiProject):
        return project
    return None


def organization_of(identity: WhoamiResponse) -> WhoamiOrganization | None:
    organization = getattr(identity, "organization", None)
    if isinstance(organization, WhoamiOrganization):
        return organization
    return None
