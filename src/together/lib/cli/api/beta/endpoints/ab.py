from __future__ import annotations

import uuid
from typing import Any, Optional
from typing_extensions import Annotated

from cyclopts import Parameter
from cyclopts.validators import Number

from together import omit
from together._utils._json import openapi_dumps
from together.types.beta.endpoint import Endpoint
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._prompt import PromptParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.endpoints.retrieve import retrieve
from together.lib.cli.api.beta.endpoints._utils._parameters import ModelParameter
from together.lib.cli.api.beta.endpoints._utils._resolve_model import (
    construct_model_path,
    resolve_model_and_config,
)
from together.lib.cli.api.beta.endpoints._utils._ab_experiments import (
    calculate_ab_members,
    find_ab_experiment_by_name,
    print_ab_experiment_detail,
)
from together.lib.cli.api.beta.endpoints._utils._resolve_config import (
    construct_config_path,
)
from together.lib.cli.api.beta.endpoints._utils._build_autoscaling import build_autoscaling
from together.lib.cli.api.beta.endpoints._utils._find_endpoint_by_deployment import find_endpoint_by_deployment


async def ab(
    model: ModelParameter,
    *,
    control: Annotated[str, Parameter(help="Control deployment ID (dep_...) currently serving live traffic")],
    percent: Annotated[
        int,
        Parameter(
            help="Percentage of live traffic to allocate to the new variant (1–99)",
            validator=Number(gte=1, lte=99),
        ),
        PromptParameter(message="Traffic percent to allocate to the new variant (1–99)"),
    ],
    config_id: Annotated[
        Optional[str],
        Parameter(
            help=(
                "Config revision ID (cr_...) for the variant deployment. Automatically selected only when one "
                "compatible config exists."
            ),
            name="config",
        ),
    ] = None,
    enable_lora: Annotated[
        bool,
        Parameter(help="Run the multi-LoRA kernel so adapters can be loaded after deployment", negative=()),
    ] = False,
    name: Annotated[
        Optional[str],
        Parameter(help="Variant deployment name; defaults to the model name with a short suffix"),
    ] = None,
    config: CLIConfigParameter,
) -> None:
    """Create a variant deployment and allocate it a percentage of live endpoint traffic."""
    endpoint = await find_endpoint_by_deployment(config.client, control)

    control_deployment = await show_loading_status(
        "Loading control deployment...",
        config.client.beta.endpoints.deployments.retrieve(
            id=control,
            endpoint_id=endpoint.id,
        ),
    )
    verify_control_receiving_traffic(endpoint, control)

    resolved = await resolve_model_and_config(config, model, config_id=config_id)
    resolved_model, config_value = resolved.model, resolved.config

    autoscaling = build_autoscaling(
        min_replicas=1,
        max_replicas=1,
        scale_up_window=None,
        scale_down_window=None,
        scaling_metrics=None,
        required=True,
    )

    if name is None:
        short_uuid = str(uuid.uuid4())[:8]
        name = f"{resolved_model.name}-{short_uuid}".replace("/", "-")

    experiment_name = build_ab_experiment_name(control_deployment.name)
    existing_experiment = await find_ab_experiment_by_name(
        config.client,
        endpoint_id=endpoint.id,
        name=experiment_name,
    )

    deployment = await show_loading_status(
        "Creating variant deployment...",
        config.client.beta.endpoints.deployments.create(
            endpoint_id=endpoint.id,
            enable_lora=enable_lora,
            name=name,
            model=construct_model_path(resolved_model, resolved.revision_id),
            config=construct_config_path(config_value),
            autoscaling=autoscaling,
        ),
    )
    assert deployment.id is not None

    members = calculate_ab_members(
        control_deployment_id=control,
        new_deployment_id=deployment.id,
        new_percent=percent,
        existing_members=existing_experiment.members if existing_experiment else None,
    )

    if existing_experiment is None:
        experiment = await show_loading_status(
            "Creating A/B experiment...",
            config.client.beta.endpoints.ab_experiments.create(
                endpoint_id=endpoint.id,
                name=experiment_name,
                members=members,
            ),
        )
    else:
        assert existing_experiment.id is not None
        experiment = await show_loading_status(
            "Updating A/B experiment...",
            config.client.beta.endpoints.ab_experiments.update(
                id=existing_experiment.id,
                endpoint_id=endpoint.id,
                update_mask="members",
                members=members,
                etag=existing_experiment.etag or omit,
            ),
        )

    if config.json:
        payload: dict[str, Any] = {"deployment": deployment, "ab_experiment": experiment}
        console.print_json(openapi_dumps(payload).decode("utf-8"))
        return

    console.print("[green]√[/green] Variant deployment created and added to A/B experiment.")
    print_ab_experiment_detail(experiment)
    await retrieve(endpoint.id, config=config)


def build_ab_experiment_name(deployment_name: str) -> str:
    return f"{deployment_name}-ab".replace("/", "-")


def verify_control_receiving_traffic(endpoint: Endpoint, control_deployment_id: str) -> None:
    traffic_split = endpoint.traffic_split or []
    if not traffic_split:
        raise ValueError(
            f"Control deployment {control_deployment_id} is not receiving traffic. "
            "Route traffic to the control deployment before starting an A/B experiment."
        )

    total_weight = sum(traffic.weight for traffic in traffic_split)
    if total_weight <= 0:
        raise ValueError(
            f"Control deployment {control_deployment_id} is not receiving traffic. "
            "Route traffic to the control deployment before starting an A/B experiment."
        )

    control_traffic = next(
        (traffic for traffic in traffic_split if traffic.deployment_id == control_deployment_id),
        None,
    )
    if control_traffic is None or control_traffic.weight <= 0:
        raise ValueError(
            f"Control deployment {control_deployment_id} is not in the endpoint traffic split. "
            "Route traffic to the control deployment before starting an A/B experiment."
        )
