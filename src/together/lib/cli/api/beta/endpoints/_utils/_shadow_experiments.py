from __future__ import annotations

from together import AsyncClient
from together.types.beta.endpoints.shadow_experiment import ShadowExperiment


async def find_shadow_for_deployment(
    client: AsyncClient,
    endpoint_id: str,
    deployment_id: str,
) -> ShadowExperiment | None:
    page = await client.beta.endpoints.shadow_experiments.list(
        endpoint_id=endpoint_id,
        include_targets=True,
    )
    for experiment in page.data:
        for target in experiment.targets or []:
            if target.target_deployment_id == deployment_id:
                return experiment
    return None
