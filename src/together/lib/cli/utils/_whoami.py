"""`GET /v3/whoami` for the CLI. The SDK's `client.whoami()` still calls `/v1/whoami`."""

from __future__ import annotations

from together.types import WhoamiProject, WhoamiResponse, WhoamiOrganization


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
