from __future__ import annotations

from together import AsyncClient
from together.types.beta.endpoints.shadow_experiment import ShadowExperiment


async def find_shadows_for_deployment(
    client: AsyncClient,
    endpoint_id: str,
    deployment_id: str,
) -> list[ShadowExperiment]:
    """Return every shadow experiment that already targets ``deployment_id``."""
    matches: list[ShadowExperiment] = []
    async for experiment in client.beta.endpoints.shadow_experiments.list(
        endpoint_id=endpoint_id,
        include_targets=True,
    ):
        if any(target.target_deployment_id == deployment_id for target in experiment.targets or []):
            matches.append(experiment)
    return matches


async def find_shadow_for_deployment(
    client: AsyncClient,
    endpoint_id: str,
    deployment_id: str,
) -> ShadowExperiment | None:
    matches = await find_shadows_for_deployment(client, endpoint_id, deployment_id)
    return matches[0] if matches else None
