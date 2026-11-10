from __future__ import annotations

import asyncio
from typing import Any, TypeVar, Coroutine
from typing_extensions import Annotated

from cyclopts import Parameter

from together import NotFoundError
from together.types import Model
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfig, CLIConfigParameter
from together.lib.cli.utils._whoami import organization_of
from together.lib.cli.utils._console import console
from together.lib.cli.api.models._utils import print_model_detail
from together.lib.cli.components.loader import show_loading_status
from together.types.model_list_files_response import ModelListFilesResponse


async def retrieve(
    id: Annotated[str, Parameter(help="Model ID to retrieve")],
    *,
    config: CLIConfigParameter,
) -> None:
    """Retrieve a model.

    Looks the model up in the current project. If that project does not have it,
    falls back to the caller's organization.
    """
    model, files = await show_loading_status("Loading model...", _load_model(config, id))

    if config.json:
        payload = model.to_dict(use_api_names=True)
        if files is not None:
            if files.revision_id:
                payload["revisionId"] = files.revision_id
            if files.revision_created_at:
                payload["revisionCreatedAt"] = files.revision_created_at
            if files.total_size_bytes:
                payload["totalSizeBytes"] = files.total_size_bytes
            payload["files"] = [file.to_dict(use_api_names=True) for file in (files.data or [])]
        console.print_json(openapi_dumps(payload).decode("utf-8"))
        return

    await print_model_detail(model, config=config, files=files)


async def _load_model(config: CLIConfig, model_id: str) -> tuple[Model, ModelListFilesResponse | None]:
    try:
        model, files = await asyncio.gather(
            config.client.models.retrieve(model_id),
            safe_fetch(config.client.models.list_files(id=model_id)),
        )
        return model, files
    except NotFoundError as project_error:
        model = await _retrieve_org_model(config, model_id, project_error)
        files = await safe_fetch(config.client.models.list_files(id=model_id, project_id=model.project_id))
        return model, files


async def _retrieve_org_model(config: CLIConfig, model_id: str, project_error: NotFoundError) -> Model:
    organization = organization_of(await config.client.whoami())
    if organization is None:
        raise project_error
    try:
        return await config.client.models.retrieve_org_model(organization.id, model_id)
    except NotFoundError:
        raise project_error from None


T = TypeVar("T")


async def safe_fetch(coro: Coroutine[Any, Any, T]) -> T | None:
    try:
        return await coro
    except Exception:
        return None
