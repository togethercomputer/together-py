from __future__ import annotations

import asyncio
import contextlib
from typing import Any
from typing_extensions import Annotated

from cyclopts import Parameter
from rich.markup import escape as escape_rich_markup

from together import APIError, AsyncClient, omit
from together.types import Endpoint, DeploymentAutoscalingParam
from together.pagination import AsyncCursorPagination
from together._utils._json import openapi_dumps
from together.lib.cli.utils._exit import CliDiagnosticExit
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.types.endpoints.ab_experiment import AbExperiment
from together.types.endpoints.shadow_experiment import ShadowExperiment
from together.types.endpoints.adapter_list_response import AdapterListResponse
from together.lib.cli.api.endpoints._utils._rollouts import resolve_rollout_by_id
from together.lib.cli.api.endpoints._utils._detach_from_experiments import (
    detach_deployment_from_experiments,
)
from together.lib.cli.api.endpoints._utils._find_endpoint_by_deployment import find_endpoint_by_deployment

# Bound how many deployment adapter lists run at once.
_ADAPTER_LIST_CONCURRENCY = 16


async def rm(
    id: Annotated[
        str,
        Parameter(help="Resource ID to delete (ep_..., dep_..., dad_..., abx_..., exp_..., or rol_...)"),
    ],
    force: Annotated[
        bool,
        Parameter(
            help=(
                "For an endpoint ID, also clear routing, scale down, and delete every child deployment before "
                "deleting the endpoint"
            )
        ),
    ] = False,
    *,
    config: CLIConfigParameter,
) -> None:
    """Smart-delete any dedicated-endpoint resource by ID prefix."""
    if id.startswith("ep_"):
        result = await _delete_endpoint(id, force=force, config=config)
    elif id.startswith("dep_"):
        result = await _delete_deployment(id, config=config)
    elif id.startswith("dad_"):
        result = await _delete_adapter(id, config=config)
    elif id.startswith("abx_"):
        result = await _delete_ab_experiment(id, config=config)
    elif id.startswith("exp_"):
        result = await _delete_shadow_experiment(id, config=config)
    elif id.startswith("rol_"):
        result = await _delete_rollout(id, config=config)
    else:
        raise ValueError(f"Unrecognized resource ID {id!r}. Expected a prefix of ep_, dep_, dad_, abx_, exp_, or rol_.")

    if config.json:
        console.print_json(openapi_dumps(result).decode("utf-8"))
        return

    console.print(f"[green]√[/green] {result['message']}")


async def _delete_endpoint(endpoint_id: str, *, force: bool, config: CLIConfigParameter) -> dict[str, Any]:
    try:
        await show_loading_status(
            "Deleting endpoint...",
            config.client.endpoints.delete(endpoint_id),
        )
    except APIError as e:
        if force:
            endpoint = await config.client.endpoints.retrieve(endpoint_id)
            await config.client.endpoints.update(endpoint_id, traffic_split=[], update_mask="trafficSplit")

            for deployment in endpoint.deployments or []:
                assert deployment.id is not None
                await config.client.endpoints.deployments.update(
                    deployment.id,
                    endpoint_id=endpoint_id,
                    autoscaling=DeploymentAutoscalingParam(min_replicas=0, max_replicas=0),
                    update_mask="autoscaling",
                )
                await config.client.endpoints.deployments.delete(deployment.id, endpoint_id=endpoint_id)

            await show_loading_status(
                "Deleting endpoint...",
                config.client.endpoints.delete(endpoint_id),
            )
        else:
            await _print_endpoint_delete_blocked(endpoint_id, error=e, config=config)
            raise CliDiagnosticExit("Endpoint deletion blocked by child deployments") from None

    return {"message": f"Deleted endpoint {endpoint_id}", "id": endpoint_id, "type": "endpoint"}


async def _print_endpoint_delete_blocked(
    endpoint_id: str,
    *,
    error: APIError,
    config: CLIConfigParameter,
) -> None:
    endpoint = await config.client.endpoints.retrieve(endpoint_id)
    deployments = [d for d in (endpoint.deployments or []) if d.id]

    if config.json:
        console.print_json(
            openapi_dumps(
                {
                    "error": error.message,
                    "id": endpoint_id,
                    "type": "endpoint",
                    "deployments": [
                        {"id": d.id, "name": getattr(d, "name", None), "command": f"tg endpoints rm {d.id}"}
                        for d in deployments
                    ],
                    "hint": "Delete each deployment first, then retry deleting the endpoint.",
                }
            ).decode("utf-8")
        )
        return

    console.print(f"[red]×[/red] Cannot delete endpoint [primary]{escape_rich_markup(endpoint_id)}[/primary].\n")
    if deployments:
        console.print("  Remove its deployments first:")
        for deployment in deployments:
            label = f" ({deployment.name})" if getattr(deployment, "name", None) else ""
            console.print(
                f"    [primary]tg endpoints rm {escape_rich_markup(deployment.id)}[/primary]"
                f"[dim]{escape_rich_markup(label)}[/dim]"
            )
        console.print(f"\n  Then retry: [primary]tg endpoints rm {escape_rich_markup(endpoint_id)}[/primary]")
    else:
        console.print(f"  [white]{escape_rich_markup(error.message)}[/white]")


async def _delete_deployment(deployment_id: str, *, config: CLIConfigParameter) -> dict[str, Any]:
    endpoint = await find_endpoint_by_deployment(config.client, deployment_id)
    actions = await detach_deployment_from_experiments(
        config,
        endpoint=endpoint,
        deployment_id=deployment_id,
    )

    try:
        await show_loading_status(
            "Deleting deployment...",
            config.client.endpoints.deployments.delete(
                id=deployment_id,
                endpoint_id=endpoint.id,
            ),
        )
    except APIError as e:
        await _scale_down_and_ask_retry(deployment_id, endpoint_id=endpoint.id, error=e, config=config)
        raise CliDiagnosticExit("Deployment deletion deferred while the deployment scales down") from None

    message = f"Deleted deployment {deployment_id}"
    if actions:
        message = f"{message} ({'; '.join(actions)})"
    return {"message": message, "id": deployment_id, "type": "deployment", "actions": actions}


async def _scale_down_and_ask_retry(
    deployment_id: str,
    *,
    endpoint_id: str,
    error: APIError,
    config: CLIConfigParameter,
) -> None:
    await show_loading_status(
        "Scaling deployment to zero...",
        config.client.endpoints.deployments.update(
            deployment_id,
            endpoint_id=endpoint_id,
            autoscaling=DeploymentAutoscalingParam(min_replicas=0, max_replicas=0),
            update_mask="autoscaling",
        ),
    )

    message = f"Deployment {deployment_id} is scaling down. Once it has stopped, retry: tg endpoints rm {deployment_id}"

    if config.json:
        console.print_json(
            openapi_dumps(
                {
                    "error": error.message,
                    "id": deployment_id,
                    "type": "deployment",
                    "status": "scaling_down",
                    "message": message,
                    "command": f"tg endpoints rm {deployment_id}",
                }
            ).decode("utf-8")
        )
        return

    console.print(
        f"[yellow]![/yellow] Deployment [primary]{escape_rich_markup(deployment_id)}[/primary] "
        "must be stopped before it can be deleted.\n"
    )
    console.print("  Scaled min/max replicas to 0 — waiting for it to stop.")
    console.print(f"  Once stopped, retry: [primary]tg endpoints rm {escape_rich_markup(deployment_id)}[/primary]")


async def _delete_adapter(adapter_id: str, *, config: CLIConfigParameter) -> dict[str, Any]:
    endpoint_id, deployment_id, adapter = await _find_adapter(config.client, adapter_id)
    await show_loading_status(
        "Removing adapter...",
        config.client.endpoints.adapters.delete(
            id=adapter.id,
            endpoint_id=endpoint_id,
            deployment_id=deployment_id,
            etag=adapter.etag,
        ),
    )
    return {"message": f"Deleted adapter {adapter_id}", "id": adapter_id, "type": "adapter"}


async def _list_endpoint_page(client: AsyncClient, after: str | None) -> AsyncCursorPagination[Endpoint]:
    # `list` returns an awaitable paginator, not a coroutine, so it cannot be passed to create_task directly.
    return await client.endpoints.list(after=after or omit)


async def _find_adapter(
    client: AsyncClient,
    adapter_id: str,
) -> tuple[str, str, AdapterListResponse]:
    """Locate an adapter attachment by scanning deployment adapter lists concurrently."""
    pending_page: asyncio.Task[AsyncCursorPagination[Endpoint]] | None = asyncio.create_task(
        _list_endpoint_page(client, None)
    )
    try:
        while pending_page is not None:
            endpoints = await pending_page
            pending_page = None
            if endpoints.next_cursor:
                # Fetch the next endpoint page while this page's deployments are scanned.
                pending_page = asyncio.create_task(_list_endpoint_page(client, endpoints.next_cursor))
            match = await _find_adapter_on_page(client, endpoints.data, adapter_id)
            if match is not None:
                return match
    finally:
        await _cancel_task(pending_page)
    raise ValueError(f"Adapter {adapter_id} not found.")


async def _find_adapter_on_page(
    client: AsyncClient,
    endpoints: list[Endpoint],
    adapter_id: str,
) -> tuple[str, str, AdapterListResponse] | None:
    targets = [
        (endpoint.id, deployment.id)
        for endpoint in endpoints
        for deployment in endpoint.deployments or []
        if deployment.id
    ]
    if not targets:
        return None

    semaphore = asyncio.Semaphore(_ADAPTER_LIST_CONCURRENCY)

    async def scan(endpoint_id: str, deployment_id: str) -> tuple[str, str, AdapterListResponse] | None:
        async with semaphore:
            try:
                # Deployments that cannot host adapters reject the list call; keep scanning.
                async for adapter in client.endpoints.adapters.list(endpoint_id, deployment_id):
                    if adapter.id == adapter_id:
                        return endpoint_id, deployment_id, adapter
            except APIError:
                return None
            return None

    tasks = [asyncio.create_task(scan(endpoint_id, deployment_id)) for endpoint_id, deployment_id in targets]
    try:
        for finished in asyncio.as_completed(tasks):
            match = await finished
            if match is not None:
                return match
        return None
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


async def _cancel_task(task: asyncio.Task[AsyncCursorPagination[Endpoint]] | None) -> None:
    if task is None:
        return
    if not task.done():
        task.cancel()
    with contextlib.suppress(asyncio.CancelledError, Exception):
        await task


async def _delete_ab_experiment(experiment_id: str, *, config: CLIConfigParameter) -> dict[str, Any]:
    endpoint_id, experiment = await _find_ab_experiment(config.client, experiment_id, config.project_id)
    await show_loading_status(
        "Deleting A/B experiment...",
        config.client.endpoints.ab_experiments.delete(
            id=experiment.id,
            endpoint_id=endpoint_id,
            etag=experiment.etag or omit,
        ),
    )
    return {"message": f"Deleted A/B experiment {experiment_id}", "id": experiment_id, "type": "ab_experiment"}


async def _delete_shadow_experiment(experiment_id: str, *, config: CLIConfigParameter) -> dict[str, Any]:
    endpoint_id, experiment = await _find_shadow_experiment(config.client, experiment_id)
    await show_loading_status(
        "Deleting shadow experiment...",
        config.client.endpoints.shadow_experiments.delete(
            id=experiment.id,
            endpoint_id=endpoint_id,
            etag=experiment.etag or omit,
        ),
    )
    return {
        "message": f"Deleted shadow experiment {experiment_id}",
        "id": experiment_id,
        "type": "shadow_experiment",
    }


async def _delete_rollout(rollout_id: str, *, config: CLIConfigParameter) -> dict[str, Any]:
    rollout = await resolve_rollout_by_id(config.client, rollout_id)
    await show_loading_status(
        "Deleting rollout...",
        config.client.endpoints.rollouts.delete(
            id=rollout.id,
            endpoint_id=rollout.endpoint_id,
            etag=rollout.etag or omit,
        ),
    )
    return {"message": f"Deleted rollout {rollout_id}", "id": rollout_id, "type": "rollout"}


async def _find_ab_experiment(
    client: AsyncClient,
    experiment_id: str,
    project_id: str | None,
) -> tuple[str, AbExperiment]:
    cursor: str | None = None
    while True:
        endpoints = await client.endpoints.list(after=cursor or omit)
        for endpoint in endpoints.data:
            page_cursor: str | None = None
            while True:
                page = await client.endpoints.ab_experiments.list(
                    endpoint_id=endpoint.id,
                    project_id=project_id,
                    after=page_cursor or omit,
                )
                for experiment in page.data:
                    if experiment.id == experiment_id:
                        return endpoint.id, experiment
                if not page.next_cursor:
                    break
                page_cursor = page.next_cursor
        if not endpoints.next_cursor:
            break
        cursor = endpoints.next_cursor
    raise ValueError(f"A/B experiment {experiment_id} not found.")


async def _find_shadow_experiment(
    client: AsyncClient,
    experiment_id: str,
) -> tuple[str, ShadowExperiment]:
    cursor: str | None = None
    while True:
        endpoints = await client.endpoints.list(after=cursor or omit)
        for endpoint in endpoints.data:
            page = await client.endpoints.shadow_experiments.list(
                endpoint_id=endpoint.id,
                include_targets=True,
            )
            for experiment in page.data:
                if experiment.id == experiment_id:
                    return endpoint.id, experiment
        if not endpoints.next_cursor:
            break
        cursor = endpoints.next_cursor
    raise ValueError(f"Shadow experiment {experiment_id} not found.")
