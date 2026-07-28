from __future__ import annotations

from typing import List, Tuple, Optional

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


async def _collect_deployment_matches(
    client: AsyncClient,
    deployment_id_or_name: str,
) -> List[Tuple[Endpoint, str]]:
    """Return ``(endpoint, deployment_id)`` for every matching deployment across all pages."""
    matches: List[Tuple[Endpoint, str]] = []
    # Deployment IDs are unique — stop once we find one. Names can collide across endpoints.
    match_by_id = deployment_id_or_name.startswith("dep_")
    cursor: Optional[str] = None
    while True:
        page = await client.beta.endpoints.list(after=cursor or omit)
        for endpoint in page.data:
            for deployment in endpoint.deployments or []:
                if _deployment_matches(deployment_id_or_name, deployment.id, deployment.name):
                    matches.append((endpoint, deployment.id))
                    if match_by_id:
                        return matches
        if not page.next_cursor:
            break
        cursor = page.next_cursor
    return matches


def _require_unique_deployment_match(
    deployment_id_or_name: str,
    matches: List[Tuple[Endpoint, str]],
) -> Tuple[Endpoint, str]:
    if not matches:
        raise ValueError(f"Deployment {deployment_id_or_name} not found in any endpoint.")
    if len(matches) > 1:
        raise ValueError(f"""Multiple deployments found for "{deployment_id_or_name}".
Please specify a deployment ID (dep_...) or a fully qualified deployment name.
""")
    return matches[0]


async def find_endpoint_by_deployment(
    client: AsyncClient,
    deployment_id_or_name: str,
) -> Endpoint:
    """Find the parent endpoint for a deployment ID (`dep_...`) or deployment name."""
    endpoint, _deployment_id = _require_unique_deployment_match(
        deployment_id_or_name,
        await _collect_deployment_matches(client, deployment_id_or_name),
    )
    return endpoint


async def resolve_deployment_id(
    client: AsyncClient,
    deployment_id_or_name: str,
) -> Tuple[Endpoint, str]:
    """Resolve a deployment ID or name to ``(parent_endpoint, deployment_id)``."""
    return _require_unique_deployment_match(
        deployment_id_or_name,
        await _collect_deployment_matches(client, deployment_id_or_name),
    )
