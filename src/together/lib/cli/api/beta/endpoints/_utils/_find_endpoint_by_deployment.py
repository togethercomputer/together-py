from __future__ import annotations

from typing import List, Tuple, Optional

from together import AsyncClient, omit
from together.types.beta import Endpoint


class AmbiguousDeploymentError(ValueError):
    """Raised when a deployment name matches more than one deployment."""


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
    if "/" in deployment_id_or_name:
        # Qualified refs must not collapse to the last segment — that makes
        # `project/endpoint/canary` collide with another endpoint's `canary`,
        # and `other-endpoint/canary` silently attach the wrong endpoint.
        return deployment_name.endswith("/" + deployment_id_or_name)
    return deployment_name.rsplit("/", 1)[-1] == deployment_id_or_name


async def _collect_deployment_matches(
    client: AsyncClient,
    deployment_id_or_name: str,
) -> List[Tuple[Endpoint, str]]:
    """Return ``(endpoint, deployment_id)`` for every matching deployment across all pages."""
    matches: List[Tuple[Endpoint, str]] = []
    cursor: Optional[str] = None
    while True:
        page = await client.beta.endpoints.list(after=cursor or omit)
        for endpoint in page.data:
            for deployment in endpoint.deployments or []:
                if _deployment_matches(deployment_id_or_name, deployment.id, deployment.name):
                    matches.append((endpoint, deployment.id))
                    # Deployment IDs are unique — stop once we find one. Names can collide.
                    if deployment.id == deployment_id_or_name:
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
        raise AmbiguousDeploymentError(f"""Multiple deployments found for "{deployment_id_or_name}".
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


async def resolve_deployment_ids(
    client: AsyncClient,
    *deployment_id_or_names: str,
) -> List[Tuple[Endpoint, str]]:
    """Resolve multiple deployment refs in a single paginated endpoint scan."""
    if not deployment_id_or_names:
        return []
    if len(deployment_id_or_names) == 1:
        return [await resolve_deployment_id(client, deployment_id_or_names[0])]

    matches: List[List[Tuple[Endpoint, str]]] = [[] for _ in deployment_id_or_names]
    # Exact ID hits are unique — stop collecting for that ref once found.
    done = [False] * len(deployment_id_or_names)
    cursor: Optional[str] = None
    while True:
        page = await client.beta.endpoints.list(after=cursor or omit)
        for endpoint in page.data:
            for deployment in endpoint.deployments or []:
                for i, ref in enumerate(deployment_id_or_names):
                    if done[i]:
                        continue
                    if _deployment_matches(ref, deployment.id, deployment.name):
                        matches[i].append((endpoint, deployment.id))
                        if deployment.id == ref:
                            matches[i] = [(endpoint, deployment.id)]
                            done[i] = True
        if all(done) or not page.next_cursor:
            break
        cursor = page.next_cursor

    return [
        _require_unique_deployment_match(ref, ref_matches) for ref, ref_matches in zip(deployment_id_or_names, matches)
    ]
