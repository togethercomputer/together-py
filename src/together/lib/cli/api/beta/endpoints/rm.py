from __future__ import annotations

import sys
from typing import Any
from typing_extensions import Annotated

from cyclopts import Parameter
from rich.markup import escape as escape_rich_markup

from together import APIError, AsyncClient, omit
from together.types.beta import AbMember, AbMemberParam, DeploymentAutoscalingParam, EndpointTrafficSplitEntryParam
from together._utils._json import openapi_dumps
from together.types.beta.endpoint import Endpoint
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.types.beta.endpoints.ab_experiment import AbExperiment
from together.types.beta.endpoints.shadow_experiment import ShadowExperiment
from together.lib.cli.api.beta.endpoints._utils._ab_experiments import find_ab_for_deployment
from together.lib.cli.api.beta.endpoints._utils._find_endpoint_by_deployment import find_endpoint_by_deployment


async def rm(
    id: Annotated[str, Parameter(help="Resource ID to delete (ep_..., dep_..., abx_..., or exp_...)")],
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
    elif id.startswith("abx_"):
        result = await _delete_ab_experiment(id, config=config)
    elif id.startswith("exp_"):
        result = await _delete_shadow_experiment(id, config=config)
    else:
        raise ValueError(f"Unrecognized resource ID {id!r}. Expected a prefix of ep_, dep_, abx_, or exp_.")

    if config.json:
        console.print_json(openapi_dumps(result).decode("utf-8"))
        return

    console.print(f"[green]√[/green] {result['message']}")


async def _delete_endpoint(endpoint_id: str, *, force: bool, config: CLIConfigParameter) -> dict[str, Any]:
    try:
        await show_loading_status(
            "Deleting endpoint...",
            config.client.beta.endpoints.delete(endpoint_id),
        )
    except APIError as e:
        if force:
            endpoint = await config.client.beta.endpoints.retrieve(endpoint_id)
            await config.client.beta.endpoints.update(endpoint_id, traffic_split=[], update_mask="trafficSplit")

            for deployment in endpoint.deployments or []:
                assert deployment.id is not None
                await config.client.beta.endpoints.deployments.update(
                    deployment.id,
                    endpoint_id=endpoint_id,
                    autoscaling=DeploymentAutoscalingParam(min_replicas=0, max_replicas=0),
                    update_mask="autoscaling",
                )
                await config.client.beta.endpoints.deployments.delete(deployment.id, endpoint_id=endpoint_id)

            await show_loading_status(
                "Deleting endpoint...",
                config.client.beta.endpoints.delete(endpoint_id),
            )
        else:
            await _print_endpoint_delete_blocked(endpoint_id, error=e, config=config)
            sys.exit(1)

    return {"message": f"Deleted endpoint {endpoint_id}", "id": endpoint_id, "type": "endpoint"}


async def _print_endpoint_delete_blocked(
    endpoint_id: str,
    *,
    error: APIError,
    config: CLIConfigParameter,
) -> None:
    endpoint = await config.client.beta.endpoints.retrieve(endpoint_id)
    deployments = [d for d in (endpoint.deployments or []) if d.id]

    if config.json:
        console.print_json(
            openapi_dumps(
                {
                    "error": error.message,
                    "id": endpoint_id,
                    "type": "endpoint",
                    "deployments": [
                        {"id": d.id, "name": getattr(d, "name", None), "command": f"tg beta endpoints rm {d.id}"}
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
                f"    [primary]tg beta endpoints rm {escape_rich_markup(deployment.id)}[/primary]"
                f"[dim]{escape_rich_markup(label)}[/dim]"
            )
        console.print(f"\n  Then retry: [primary]tg beta endpoints rm {escape_rich_markup(endpoint_id)}[/primary]")
    else:
        console.print(f"  [white]{escape_rich_markup(error.message)}[/white]")


async def _delete_deployment(deployment_id: str, *, config: CLIConfigParameter) -> dict[str, Any]:
    endpoint = await find_endpoint_by_deployment(config.client, deployment_id)
    actions: list[str] = []

    shadow = await _find_shadow_for_deployment(config.client, endpoint.id, deployment_id)
    if shadow is not None:
        target = next(t for t in (shadow.targets or []) if t.target_deployment_id == deployment_id)
        await show_loading_status(
            "Removing deployment from shadow experiment...",
            config.client.beta.endpoints.shadow_experiments.targets.delete(
                id=target.id,
                endpoint_id=endpoint.id,
                experiment_id=shadow.id,
                etag=target.etag or omit,
            ),
        )
        remaining = [t for t in (shadow.targets or []) if t.target_deployment_id != deployment_id]
        if remaining:
            actions.append(f"removed from shadow experiment {shadow.id}")
        else:
            await show_loading_status(
                "Deleting empty shadow experiment...",
                config.client.beta.endpoints.shadow_experiments.delete(
                    id=shadow.id,
                    endpoint_id=endpoint.id,
                    etag=shadow.etag or omit,
                ),
            )
            actions.append(f"deleted empty shadow experiment {shadow.id}")

    ab = await find_ab_for_deployment(config.client, endpoint.id, deployment_id)
    if ab is not None:
        removed = next(m for m in ab.members if m.deployment_id == deployment_id)
        remaining_members = [m for m in ab.members if m.deployment_id != deployment_id]
        # A/B experiments require >= 2 members and a control; otherwise delete the experiment.
        if len(remaining_members) < 2 or removed.role == "AB_EXPERIMENT_MEMBER_ROLE_CONTROL":
            await show_loading_status(
                "Deleting A/B experiment...",
                config.client.beta.endpoints.ab_experiments.delete(
                    id=ab.id,
                    endpoint_id=endpoint.id,
                    etag=ab.etag or omit,
                ),
            )
            actions.append(f"deleted A/B experiment {ab.id}")
        else:
            members = _members_without_deployment(ab.members, deployment_id)
            await show_loading_status(
                "Removing deployment from A/B experiment...",
                config.client.beta.endpoints.ab_experiments.update(
                    id=ab.id,
                    endpoint_id=endpoint.id,
                    update_mask="members",
                    members=members,
                    etag=ab.etag or omit,
                ),
            )
            actions.append(f"removed from A/B experiment {ab.id}")

    await _detach_from_traffic_split(config.client, endpoint, deployment_id)

    try:
        await show_loading_status(
            "Deleting deployment...",
            config.client.beta.endpoints.deployments.delete(
                id=deployment_id,
                endpoint_id=endpoint.id,
            ),
        )
    except APIError as e:
        await _scale_down_and_ask_retry(deployment_id, endpoint_id=endpoint.id, error=e, config=config)
        sys.exit(1)

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
        config.client.beta.endpoints.deployments.update(
            deployment_id,
            endpoint_id=endpoint_id,
            autoscaling=DeploymentAutoscalingParam(min_replicas=0, max_replicas=0),
            update_mask="autoscaling",
        ),
    )

    message = (
        f"Deployment {deployment_id} is scaling down. Once it has stopped, retry: tg beta endpoints rm {deployment_id}"
    )

    if config.json:
        console.print_json(
            openapi_dumps(
                {
                    "error": error.message,
                    "id": deployment_id,
                    "type": "deployment",
                    "status": "scaling_down",
                    "message": message,
                    "command": f"tg beta endpoints rm {deployment_id}",
                }
            ).decode("utf-8")
        )
        return

    console.print(
        f"[yellow]![/yellow] Deployment [primary]{escape_rich_markup(deployment_id)}[/primary] "
        "must be stopped before it can be deleted.\n"
    )
    console.print("  Scaled min/max replicas to 0 — waiting for it to stop.")
    console.print(f"  Once stopped, retry: [primary]tg beta endpoints rm {escape_rich_markup(deployment_id)}[/primary]")


async def _delete_ab_experiment(experiment_id: str, *, config: CLIConfigParameter) -> dict[str, Any]:
    endpoint_id, experiment = await _find_ab_experiment(config.client, experiment_id, config.project_id)
    await show_loading_status(
        "Deleting A/B experiment...",
        config.client.beta.endpoints.ab_experiments.delete(
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
        config.client.beta.endpoints.shadow_experiments.delete(
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


def _members_without_deployment(members: list[AbMember], deployment_id: str) -> list[AbMemberParam]:
    removed = next((m for m in members if m.deployment_id == deployment_id), None)
    if removed is None:
        raise ValueError(f"Deployment {deployment_id} is not a member of the A/B experiment.")

    remaining = [m for m in members if m.deployment_id != deployment_id]
    result: list[AbMemberParam] = []
    for member in remaining:
        percent = member.percent
        if member.role == "AB_EXPERIMENT_MEMBER_ROLE_CONTROL":
            percent = member.percent + removed.percent
        result.append(AbMemberParam(deployment_id=member.deployment_id, role=member.role, percent=percent))
    return result


async def _detach_from_traffic_split(client: AsyncClient, endpoint: Endpoint, deployment_id: str) -> None:
    traffic_split = endpoint.traffic_split or []
    if not any(t.deployment_id == deployment_id for t in traffic_split):
        return

    updated: list[EndpointTrafficSplitEntryParam] = [
        EndpointTrafficSplitEntryParam(deployment_id=t.deployment_id, weight=t.weight)
        for t in traffic_split
        if t.deployment_id != deployment_id
    ]
    await client.beta.endpoints.update(
        endpoint.id,
        traffic_split=updated,
        update_mask="trafficSplit",
        etag=endpoint.etag or omit,
    )


async def _find_shadow_for_deployment(
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


async def _find_ab_experiment(
    client: AsyncClient,
    experiment_id: str,
    project_id: str | None,
) -> tuple[str, AbExperiment]:
    cursor: str | None = None
    while True:
        endpoints = await client.beta.endpoints.list(after=cursor or omit)
        for endpoint in endpoints.data:
            page_cursor: str | None = None
            while True:
                page = await client.beta.endpoints.ab_experiments.list(
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
        endpoints = await client.beta.endpoints.list(after=cursor or omit)
        for endpoint in endpoints.data:
            page = await client.beta.endpoints.shadow_experiments.list(
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
