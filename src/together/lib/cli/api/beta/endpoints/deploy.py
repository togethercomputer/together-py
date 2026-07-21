from __future__ import annotations

import uuid
from typing import Any, Optional
from typing_extensions import Annotated

from cyclopts import Parameter
from rich.panel import Panel
from rich.table import Table
from cyclopts.validators import Number

from together import APIError, omit
from together.types.beta import Model, Endpoint, DeploymentAutoscalingParam
from together._utils._json import openapi_dumps
from together.types.beta.models import Config
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._prompt import PromptParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.endpoints.retrieve import retrieve
from together.lib.cli.utils._assert_explicit_project_id import assert_explicit_project_id
from together.lib.cli.api.beta.endpoints._utils._parameters import (
    ModelParameter,
    PlacementGroup,
    PlacementModel,
    placement_model,
)
from together.types.beta.endpoints.deployment_create_params import (
    Placement,
    PlacementProfile,
)
from together.lib.cli.api.beta.endpoints._utils._resolve_model import (
    construct_model_path,
    resolve_model_and_config,
)
from together.lib.cli.api.beta.endpoints._utils._traffic_split import upsert_traffic_weight
from together.lib.cli.api.beta.endpoints._utils._resolve_config import (
    construct_config_path,
)
from together.lib.cli.api.beta.endpoints._utils._build_autoscaling import (
    ScalingMetricName,
    ScalingPercentile,
    build_autoscaling,
    build_scaling_metrics,
)

EndpointParameter = Annotated[
    str,
    Parameter(
        name="endpoint",
        help="""Endpoint that will contain the deployment.

- Pass an existing endpoint name or ID (ep_...) to add a deployment to it.
- Pass a new name to create the endpoint first. This name becomes the endpoint's immutable endpoint string.""",
    ),
    PromptParameter(instructions="What name would you like to use for your endpoint?", message="Endpoint Name"),
]
DeploymentNameParameter = Annotated[
    Optional[str],
    Parameter(help="Name for the new deployment; defaults to the model name plus a short unique suffix"),
]


# Deploy logic:
# - Create or find the referenced endpoint.
# - Resolve the supplied model input to a fully qualified model path
# - Resolve the config
#   - If the user provided a config ID, resolve the full path for it
#   - If they didn't, for public models use the model profile if the profiles array only has one item. If there are multiple, prompt the user to select one. Or print out an error message with the options they can use.
#   - If they didn't and it's a private model, call the configs model API with the model ID to get a list of configs that can be used.
async def deploy(
    model: ModelParameter,
    *,
    endpoint_name_or_id: EndpointParameter,
    config_id: Annotated[
        Optional[str],
        Parameter(
            help=(
                "Config revision ID (cr_...) for this model. The CLI selects it automatically when exactly one "
                "compatible config exists; otherwise use `tg beta models configs <MODEL_ID>` and pass one explicitly."
            ),
            name="config",
        ),
    ] = None,
    min_replicas: Annotated[
        Optional[int], Parameter(help="Minimum replicas to keep running; set both replica bounds to 0 to start stopped")
    ] = 1,
    max_replicas: Annotated[
        Optional[int], Parameter(help="Maximum replicas allowed; must be greater than or equal to --min-replicas")
    ] = 1,
    scale_up_window: Annotated[
        Optional[str],
        Parameter(
            help="How long the metric must stay above the target before adding replicas (seconds, e.g. 30 or 30s). Prevents thrashing from brief spikes."
        ),
    ] = None,
    scale_down_window: Annotated[
        Optional[str],
        Parameter(
            help="Cooldown after scaling down before removing more replicas (seconds, e.g. 60 or 60s). Higher values improve stability."
        ),
    ] = None,
    scale_to_zero_window: Annotated[
        Optional[str],
        Parameter(help="Idle time before scaling to zero replicas (seconds, e.g. 300 or 300s)."),
    ] = None,
    scaling_metric: Annotated[
        Optional[ScalingMetricName],
        Parameter(
            help=(
                """Autoscaling metric. Must be set with --scaling-target; --scaling-percentile is optional and only applies to latency metrics.

- inflight_requests: Concurrent in-flight requests per replica.
- gpu_utilization: GPU compute utilization (%).
- token_utilization: KV-cache utilization (%).
- cache_hit_rate: Prompt-cache hit rate (%).
- throughput_per_replica: Generated tokens per second per replica.
- ttft: Time to first token (ms).
- decoding_speed: Time per output token (ms).
- e2e_latency: End-to-end request latency (ms)."""
            ),
        ),
    ] = None,
    scaling_target: Annotated[
        Optional[float],
        Parameter(
            help=(
                "Target for --scaling-metric. Utilization metrics use 0–100; "
                "value/average metrics use the metric's native unit."
            ),
            validator=Number(gte=0),
        ),
    ] = None,
    scaling_percentile: Annotated[
        Optional[ScalingPercentile],
        Parameter(
            help=(
                "Optional percentile for ttft, decoding_speed, or e2e_latency. "
                "Choices: p50, p90, p95, or p99; the platform default is p95."
            ),
        ),
    ] = None,
    deployment_name: DeploymentNameParameter = None,
    model_revision: Annotated[
        Optional[str],
        Parameter(
            help=(
                "Deprecated model revision ID to pin. Prefer a fully qualified model path ending in "
                "/revisions/<REVISION_ID>."
            )
        ),
    ] = None,
    placement_id: Annotated[
        Optional[str], Parameter(name="placement", help="Placement profile ID to use", group=PlacementGroup)
    ] = None,
    placement: Annotated[PlacementModel, Parameter(group=PlacementGroup)] = placement_model,
    enable_lora: Annotated[
        Optional[bool],
        Parameter(
            negative=(),
            help="Runs the multi-LoRA kernel so adapters hot-load after deploy. Toggling later needs a redeploy.",
        ),
    ] = None,
    traffic_weight: Annotated[
        Optional[float],
        Parameter(
            help=(
                "Relative capacity weight for this deployment in the endpoint's live traffic split. "
                "Preserves other deployment weights; set to 0 for no live traffic, or omit to leave routing unchanged."
            ),
            validator=Number(gte=0),
        ),
    ] = None,
    config: CLIConfigParameter,
) -> None:
    """Create a deployment on a new or existing dedicated inference endpoint."""
    resolved_model, config_value = await resolve_model_and_config(config, model, config_id=config_id)

    autoscaling = build_autoscaling(
        min_replicas=min_replicas,
        max_replicas=max_replicas,
        scale_up_window=scale_up_window,
        scale_down_window=scale_down_window,
        scale_to_zero_window=scale_to_zero_window,
        scaling_metrics=build_scaling_metrics(
            scaling_metric=scaling_metric,
            scaling_target=scaling_target,
            scaling_percentile=scaling_percentile,
        ),
        required=True,
    )

    if deployment_name is None:
        short_uuid = str(uuid.uuid4())[:8]
        deployment_name = f"{resolved_model.name}-{short_uuid}".replace("/", "-")

    placement_value: Placement | None = None
    if placement_id:
        placement_value = PlacementProfile(profile=placement_id)
    else:
        placement_value = placement.to_json()

    if not config.json:
        _print_deployment_preview(
            endpoint=endpoint_name_or_id,
            deployment_name=deployment_name,
            model=resolved_model,
            config_value=config_value,
            autoscaling=autoscaling,
            placement=placement_value,
            enable_lora=enable_lora,
            model_revision=model_revision,
            traffic_weight=traffic_weight,
        )
    await assert_explicit_project_id(config)

    endpoint, is_new_endpoint = await _find_or_create_endpoint(config, endpoint_name_or_id)

    try:
        deployment = await show_loading_status(
            "Creating beta endpoint deployment...",
            config.client.beta.endpoints.deployments.create(
                endpoint.id,
                name=deployment_name,
                model=construct_model_path(resolved_model),
                config=construct_config_path(config_value),
                autoscaling=autoscaling,
                enable_lora=enable_lora if enable_lora is not None else omit,
                model_revision_id=model_revision or omit,
                placement=placement_value or omit,
            ),
        )
    except Exception as e:
        if is_new_endpoint:
            await config.client.beta.endpoints.delete(endpoint.id)
            console.print(f"Error creating deployment. Rolling back.")
        raise e

    if traffic_weight is not None:
        assert deployment.id is not None
        traffic_split = upsert_traffic_weight(
            endpoint.traffic_split,
            deployment_id=deployment.id,
            weight=traffic_weight,
        )
        endpoint = await show_loading_status(
            "Updating endpoint traffic split...",
            config.client.beta.endpoints.update(
                endpoint.id,
                traffic_split=traffic_split,
                update_mask="trafficSplit",
                etag=endpoint.etag or omit,
            ),
        )

    if config.json:
        payload: dict[str, Any] = {"endpoint": endpoint, "deployment": deployment}
        console.print_json(openapi_dumps(payload).decode("utf-8"))
        return

    console.print(f"\n[green]√[/green] Model deployed to endpoint {endpoint.name}.\n\n")
    await retrieve(endpoint.id, config=config)


def _print_deployment_preview(
    *,
    endpoint: str,
    deployment_name: str,
    model: Model,
    config_value: Config,
    autoscaling: DeploymentAutoscalingParam,
    placement: Placement | None,
    enable_lora: bool | None,
    model_revision: str | None,
    traffic_weight: float | None,
) -> None:
    table = Table(expand=True, show_header=False, show_edge=False, show_lines=False, box=None, pad_edge=False)
    table.add_column("Arg", justify="left", no_wrap=True, ratio=1)

    args: list[str] = []

    def add_row(flag: str, value: str) -> None:
        args.append(f"[primary]{flag}[/primary] {value}")

    add_row("--endpoint", endpoint)
    add_row("--deployment-name", deployment_name)

    if (min_replicas := autoscaling.get("min_replicas")) is not None:
        add_row("--min-replicas", str(min_replicas))
    if (max_replicas := autoscaling.get("max_replicas")) is not None:
        add_row("--max-replicas", str(max_replicas))
    if scale_up := autoscaling.get("scale_up_window"):
        add_row("--scale-up-window", str(scale_up))
    if scale_down := autoscaling.get("scale_down_window"):
        add_row("--scale-down-window", str(scale_down))
    if scale_to_zero := autoscaling.get("scale_to_zero_window"):
        add_row("--scale-to-zero-window", str(scale_to_zero))
    if metrics := autoscaling.get("scaling_metrics"):
        metric = next(iter(metrics))
        add_row("--scaling-metric", metric["name"])
        add_row("--scaling-target", str(metric["target"]))
        if percentile := metric.get("percentile"):
            add_row("--scaling-percentile", percentile)

    if model_revision:
        add_row("--model-revision", model_revision)

    if placement is not None:
        if "profile" in placement:
            add_row("--placement", placement["profile"])  # type: ignore[typeddict-item]
        else:
            inline = placement.get("inline") or {}
            if regions := inline.get("regions"):
                add_row("--regions", ",".join(regions))
            if constraint := inline.get("constraint"):
                add_row(
                    "--constraint",
                    "required" if constraint == "ENFORCEMENT_REQUIRED" else "preferred",
                )
            if inline.get("hipaa"):
                add_row("--hipaa", "true")

    if enable_lora is not None:
        add_row("--enable-lora", "true" if enable_lora else "false")
    if traffic_weight is not None:
        add_row("--traffic-weight", str(traffic_weight))
    add_row("--model", model.name)
    add_row("--config", config_value.id)  # type: ignore

    table.add_row("\n".join(args))

    console.print(
        Panel(
            table,
            title="Deploy [bold][primary]preview[/primary][/bold]",
            title_align="left",
        )
    )


# Helper method to enable the users to use this command to either create a new endpoint+deployment
# or append a new deployment to an existing endpoint
async def _find_or_create_endpoint(config: CLIConfigParameter, endpoint_input: str) -> tuple[Endpoint, bool]:
    # If the user gave us an endpoint ID, we can just retrieve it.
    if endpoint_input.startswith("ep_"):
        endpoint = await config.client.beta.endpoints.retrieve(id=endpoint_input)
        return endpoint, False

    # If the user gave us an endpoint name, we need to try to create it.
    # The API will fail if the name conflicts, in which case we know the intent is to reuse
    # an existing endpoint.
    #
    # The exception block will then search through the endpoints for the matching name.
    try:
        endpoint = await config.client.beta.endpoints.create(name=endpoint_input)
        return endpoint, True
    except APIError as e:
        me = await config.client.whoami()
        # Endpoint names in API include the project slug, so we add it if the user did not provide it.
        endpoint_name = (
            f"{me.project_slug}/{endpoint_input}" if not endpoint_input.startswith(me.project_slug) else endpoint_input
        )
        if "already exists" in e.message.lower():
            # TODO: Paginate through the endpoints and find the matching name.
            endpoints = await config.client.beta.endpoints.list()
            for endpoint in endpoints.data:
                if endpoint.name == endpoint_name:
                    return endpoint, False
        raise e
