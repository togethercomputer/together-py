from __future__ import annotations

from typing import Any, TypeVar, Coroutine
from typing_extensions import Annotated

from cyclopts import Parameter

from together import NotFoundError
from together.types import Model
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfig, CLIConfigParameter
from together.lib.cli.utils._whoami import project_of, organization_of
from together.lib.cli.utils._console import console
from together.lib.cli.api.models._utils import print_model_detail
from together.lib.cli.components.loader import show_loading_status
from together.types.model_list_files_response import ModelListFilesResponse
from together.lib.cli.api.models._resolve_base_model import resolve_supported_model_location
from together.lib.cli.api.endpoints._utils._resolve_model import MODEL_PATH_RE, _find_private_model_by_name


async def retrieve(
    id: Annotated[str, Parameter(help="Model ID (ml_...) or name (org/model from `tg models public`)")],
    *,
    config: CLIConfigParameter,
) -> None:
    """Retrieve a model.

    Looks the model up in the current project. If that project does not have it,
    falls back to the caller's organization. A name from ``tg models public``
    (or ``<project-slug>/<name>``) is resolved to that model record.
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
    if "/" in model_id:
        return await _load_named_model(config, model_id)

    try:
        model = await config.client.models.retrieve(model_id)
    except NotFoundError as project_error:
        model = await _retrieve_org_model(config, model_id, project_error)

    # Wait for the model so a failed project lookup never starts a file list, and an
    # org fallback lists files from the project that actually owns the model.
    files = await safe_fetch(config.client.models.list_files(id=model.id, project_id=model.project_id))
    return model, files


async def _load_named_model(config: CLIConfig, name: str) -> tuple[Model, ModelListFilesResponse | None]:
    path_match = MODEL_PATH_RE.match(name)
    if path_match:
        model = await config.client.models.retrieve(id=path_match.group(2), project_id=path_match.group(1))
        files = await safe_fetch(config.client.models.list_files(id=model.id, project_id=model.project_id))
        return model, files

    owned = await _load_project_model_by_name(config, name)
    if owned is not None:
        return owned

    project_id, model_id = await resolve_supported_model_location(config, name)
    try:
        model = await config.client.models.retrieve(id=model_id, project_id=project_id)
    except NotFoundError:
        raise ValueError(f'Model "{name}" resolved to {model_id} but was not found in project {project_id}.') from None
    files = await safe_fetch(config.client.models.list_files(id=model.id, project_id=model.project_id))
    return model, files


async def _load_project_model_by_name(
    config: CLIConfig, name: str
) -> tuple[Model, ModelListFilesResponse | None] | None:
    project = project_of(await config.client.whoami())
    if project is None or name.partition("/")[0] != project.slug:
        return None
    try:
        model = await _find_private_model_by_name(config, name)
    except ValueError as exc:
        if "Multiple models found" in str(exc):
            raise
        return None
    files = await safe_fetch(config.client.models.list_files(id=model.id, project_id=model.project_id))
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
