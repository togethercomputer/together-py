from __future__ import annotations

import asyncio
from collections.abc import Iterable

from together.types.beta import Endpoint
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.api.beta.endpoints._utils._resolve_model import MODEL_PATH_RE


async def resolve_model_names(endpoints: Iterable[Endpoint], config: CLIConfigParameter) -> dict[str, str]:
    """Resolve model display names without running deployment config selection."""
    model_resource_paths = {
        (deployment.model, deployment.api_model_id)
        for endpoint in endpoints
        for deployment in endpoint.deployments or []
        if deployment.model and deployment.api_model_id
    }

    async def fetch_model_name(model_resource_path: str, model_id: str) -> tuple[str, str]:
        try:
            match = MODEL_PATH_RE.match(model_resource_path)
            if match is None:
                return model_id, model_id
            project_id, model_id = match.group(1), match.group(2)
            model = await config.client.beta.models.retrieve(model_id, project_id=project_id)
            return model_id, model.name
        except Exception:
            return model_id, model_id

    return dict(
        await asyncio.gather(
            *(fetch_model_name(model_resource_path, model_id) for model_resource_path, model_id in model_resource_paths)
        )
    )
