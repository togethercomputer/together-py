"""Identity helpers for the CLI. `client.whoami()` calls `GET /v3/whoami`."""

from __future__ import annotations

from together import AsyncTogether
from together.types import (
    WhoamiUser,
    WhoamiAPIKey,
    WhoamiProject,
    WhoamiUserJwt,
    WhoamiResponse,
    WhoamiOrgAPIKey,
    WhoamiUserOrgJwt,
    WhoamiOrganization,
    WhoamiProjectAPIKey,
    WhoamiUserOrgProjectJwt,
)

# Names the CLI used before the SDK exported the discriminated whoami models.
WhoamiApiKey = WhoamiAPIKey
WhoamiOrgApiKey = WhoamiOrgAPIKey
WhoamiProjectApiKey = WhoamiProjectAPIKey

__all__ = [
    "WhoamiApiKey",
    "WhoamiAPIKey",
    "WhoamiOrganization",
    "WhoamiProject",
    "WhoamiUser",
    "WhoamiProjectApiKey",
    "WhoamiProjectAPIKey",
    "WhoamiOrgApiKey",
    "WhoamiOrgAPIKey",
    "WhoamiUserJwt",
    "WhoamiUserOrgJwt",
    "WhoamiUserOrgProjectJwt",
    "WhoamiResponse",
    "fetch_whoami",
    "project_of",
    "organization_of",
]


async def fetch_whoami(client: AsyncTogether) -> WhoamiResponse:
    """Identity of the client's credentials (API key or `tg login` token) from `/v3/whoami`."""
    return await client.whoami()


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
