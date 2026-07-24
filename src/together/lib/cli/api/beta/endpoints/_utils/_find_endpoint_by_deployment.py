from __future__ import annotations

from typing import Tuple, Optional

from together import AsyncClient, omit
from together.types.beta import Endpoint


def _deployment_matches(deployment_id_or_name: str, deployment_id: str, deployment_name: Optional[str]) -> bool:
    if deployment_id == deployment_id_or_name:
        return True
    # IDs only match on the id field — never fall through to name equality.
    if deployment_id_or_name.startswith("dep_"):
        return False
    if deployment_name is None:
        return False
    if deployment_name == deployment_id_or_name:
        return True
    return deployment_name.rsplit("/", 1)[-1] == deployment_id_or_name.rsplit("/", 1)[-1]


async def find_endpoint_by_deployment(
    client: AsyncClient,
    deployment_id_or_name: str,
) -> Endpoint:
    """Find the parent endpoint for a deployment ID (`dep_...`) or deployment name."""
    cursor: Optional[str] = None
    while True:
        page = await client.beta.endpoints.list(after=cursor or omit)
        for endpoint in page.data:
            for deployment in endpoint.deployments or []:
                if _deployment_matches(deployment_id_or_name, deployment.id, deployment.name):
                    return endpoint
        if not page.next_cursor:
            break
        cursor = page.next_cursor

    raise ValueError(f"Deployment {deployment_id_or_name} not found in any endpoint.")


async def resolve_deployment_id(
    client: AsyncClient,
    deployment_id_or_name: str,
) -> Tuple[Endpoint, str]:
    """Resolve a deployment ID or name to ``(parent_endpoint, deployment_id)``."""
    endpoint = await find_endpoint_by_deployment(client, deployment_id_or_name)
    for deployment in endpoint.deployments or []:
        if _deployment_matches(deployment_id_or_name, deployment.id, deployment.name):
            return endpoint, deployment.id
    raise ValueError(f"Deployment {deployment_id_or_name} not found in any endpoint.")
