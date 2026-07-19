from __future__ import annotations

import asyncio
from typing import List, Iterable, Optional
from typing_extensions import Annotated

from cyclopts import Parameter

from together import omit
from together.types.beta import EndpointDeploymentSummary
from together._utils._json import openapi_dumps
from together.types.beta.endpoint import Endpoint
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.utils._mock_pagination import AfterParameter
from together.lib.cli.api.beta.endpoints._utils._resolve_model import resolve_model


async def _resolve_model_names(endpoints: List[Endpoint], config: CLIConfigParameter) -> dict[str, str]:
    model_ids = {
        deployment.api_model_id
        for endpoint in endpoints
        for deployment in endpoint.deployments or []
        if deployment.api_model_id
    }

    async def fetch_model_name(model_id: str) -> tuple[str, str]:
        try:
            # TODO: We should be able to just do a GET on the deployment.api_model instead of trying to resolve from the id.
            return model_id, (await resolve_model(config, model_id)).name
        except Exception:
            return model_id, model_id

    return dict(await asyncio.gather(*(fetch_model_name(model_id) for model_id in model_ids)))


def _print_next_page(next_cursor: str | None, *, public: bool = False, org: bool = False) -> None:
    if not next_cursor:
        return
    flags = ""
    if public:
        flags = " --public"
    elif org:
        flags = " --org"
    console.print("\n[blue dim]To display the next page, run:[/blue dim]")
    console.print(f"  [dim]-[/dim] [white]tg beta endpoints ls{flags} --after {next_cursor}[/white]")


async def list(
    org: Annotated[bool, Parameter(help="List org-scoped endpoints")] = False,
    limit: Annotated[Optional[int], Parameter(help="Maximum endpoints to return")] = None,
    after: AfterParameter = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List beta endpoints for a project."""
    if org:
        message = "No org-scoped endpoints found."
        me = await config.client.whoami()
        response = await show_loading_status(
            "Loading org-scoped endpoints...",
            config.client.beta.endpoints.list_org_scoped(
                organization_id=me.organization_id,
                limit=limit if limit is not None else omit,
                after=after or omit,
            ),
        )
    else:
        message = """No dedicated inference endpoints found. To create one, run:
  [dim]-[/dim] [primary]tg beta endpoints deploy <MODEL_ID> --endpoint <ENDPOINT_NAME>[/primary]"""
        response = await show_loading_status(
            "Loading beta endpoints...",
            config.client.beta.endpoints.list(
                limit=limit if limit is not None else omit,
                after=after or omit,
            ),
        )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    data = response.data or []
    print_endpoints_table(data, model_names=await _resolve_model_names(data, config), empty_message=message)
    _print_next_page(response.next_cursor, org=org)


def print_endpoints_table(
    endpoints: Iterable[Endpoint],
    *,
    model_names: dict[str, str],
    empty_message: str,
) -> None:
    table = ListTable(empty_message=empty_message, show_lines=False)
    table.add_column("ID", width=24)
    table.add_primary_column("Name", ratio=2)
    table.add_column("Model", ratio=2)
    table.add_column("GPU")
    table.add_column("Replicas")

    for endpoint in endpoints:
        deployments = endpoint.deployments or []
        endpoint_name = _short_name(endpoint.name)

        if len(deployments) <= 1:
            deployment = deployments[0] if deployments else None
            table.add_row(
                *_endpoint_row_values(
                    endpoint,
                    deployment,
                    model_names=model_names,
                    name=endpoint_name,
                    show_id=True,
                )
            )
            table.add_row()
            continue

        primary_deployment = deployments[0]
        table.add_row(
            *_endpoint_row_values(
                endpoint,
                primary_deployment,
                model_names=model_names,
                name=endpoint_name,
                hide_details=True,
                show_id=True,
            )
        )
        for deployment in deployments:
            table.add_row(
                *_endpoint_row_values(
                    endpoint,
                    deployment,
                    model_names=model_names,
                    name=f"  └ {_short_name(deployment.name)}",
                    hide_details=False,
                )
            )
        table.add_row()

    console.print(table)


def _short_name(fully_qualified_name: str) -> str:
    return fully_qualified_name.rsplit("/", 1)[-1]


def _endpoint_row_values(
    endpoint: Endpoint,
    deployment: EndpointDeploymentSummary | None,
    *,
    model_names: dict[str, str],
    name: str,
    hide_details: bool = False,
    show_id: bool = False,
) -> tuple[str, str, str, str, str]:
    url = f"https://api.together.ai/endpoints/{endpoint.id}"
    id_cell = f"[link={url}]{endpoint.id}[/link]" if show_id else ""

    if hide_details:
        return id_cell, name, "", "", ""
    model_name = ""
    gpu = ""
    replicas = ""
    if deployment is not None:
        model_name = _truncate(model_names.get(deployment.api_model_id, deployment.api_model_id))
        gpu = _prettify_hardware(deployment.hardware)
        replicas = _format_replicas(deployment)
    return id_cell, name, model_name, gpu, replicas


def _truncate(text: str, max_len: int = 30) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def _format_replicas(deployment: EndpointDeploymentSummary) -> str:
    if deployment.state in {"DEPLOYMENT_STATE_STOPPED", "DEPLOYMENT_STATE_STOPPING"}:
        return "[dim]—[/dim]"
    ready = deployment.ready_replicas or 0
    desired = deployment.desired_replicas or 0
    if ready == desired and ready > 0:
        return f"[green]•[/green] {ready}/{desired} ready"
    return f"{ready}/{desired} ready"


def _prettify_hardware(hardware: str) -> str:
    import re

    match = re.search(r"(\d+)x(.*)", hardware)
    if match:
        count, hw_type = match.groups()
        parts = hw_type.split("-")
        return f"{count}x {' '.join(parts[1:]).upper()}"
    return hardware.replace("_", " ").title()
