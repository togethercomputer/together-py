from __future__ import annotations

import uuid
from typing import Any, Optional
from typing_extensions import Annotated

from cyclopts import Parameter
from rich.panel import Panel
from rich.table import Table
from cyclopts.validators import Number

from together import ConflictError, omit
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
    MODEL_PATH_RE,
    resolve_endpoint,
    construct_model_path,
    resolve_model_and_config,
)
from together.lib.cli.api.beta.endpoints._utils._traffic_split import upsert_traffic_weight
from together.lib.cli.api.beta.endpoints._utils._adapter_deploy import (
    load_base_model,
    list_model_configs,
    load_adapter_model,
    select_lora_config_for_deploy,
    find_compatible_deployment,
)
from together.lib.cli.api.beta.endpoints._utils._resolve_config import (
    construct_config_path,
)
from together.lib.cli.api.beta.endpoints._utils._hardware_pricing import (
    HardwarePricing,
    resolve_hardware_pricing,
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
                "compatible config exists. When several exist, pass one explicitly or pick it at the prompt."
            ),
            name="config",
        ),
    ] = None,
    min_replicas: Annotated[
        Optional[int],
        Parameter(
            help=(
                "Minimum replicas to keep running. Defaults to 1 when omitted. "
                "If only this flag is set, max replicas matches it (including 0 to start stopped)."
            )
        ),
    ] = None,
    max_replicas: Annotated[
        Optional[int],
        Parameter(
            help=(
                "Maximum replicas allowed; must be greater than or equal to --min-replicas. "
                "Defaults to the min replicas value when omitted (or 1 when neither flag is set). "
                "Passing only --max-replicas 0 also sets min replicas to 0."
            )
        ),
    ] = None,
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
    scaling_metric: Annotated[
        Optional[ScalingMetricName],
        Parameter(
            help=(
                """Autoscaling metric. Must be set with --scaling-target; --scaling-percentile is optional and only applies to latency metrics.

- active_sessions: Active sessions across the deployment.
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
    inactive_timeout: Annotated[
        Optional[int],
        Parameter(
            help="Minutes of inactivity before the deployment auto-stops (0 to disable; otherwise 30-1440).",
            validator=Number(gte=0, lte=1440),
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
    merge: Annotated[
        bool,
        Parameter(
            negative=False,
            help=(
                "For a LoRA adapter model, create a new deployment that serves the adapter merged into its "
                "base model. Adapter models require either --merge or --attach-adapter."
            ),
        ),
    ] = False,
    attach_adapter: Annotated[
        bool,
        Parameter(
            negative=False,
            help=(
                "For a LoRA adapter model, attach the adapter to a base-model deployment whose config has "
                "adapter_mode dynamic or fixed, creating that deployment when none exists. "
                "If several configs can host the adapter, pass --config or pick one at the prompt. "
                "Adapter models require either --merge or --attach-adapter."
            ),
        ),
    ] = False,
    config: CLIConfigParameter,
) -> None:
    """Create a deployment on a new or existing dedicated inference endpoint.

    When the model is a LoRA adapter (`weights.type` is `WEIGHTS_TYPE_ADAPTER`), pass exactly one of:

    - `--merge`: create a new deployment of the adapter itself, which the API merges into its base model.
    - `--attach-adapter`: attach it to an existing deployment of its base model whose config has
      `adapter_mode` dynamic or fixed. An existing dynamic deployment is preferred over a fixed one.
      With `--deployment-name`, use the deployment of that name when it exists. If the endpoint has
      no such deployment, create one. When more than one fixed or dynamic config exists and
      `--config` was not passed, the command prompts for a config, or fails in non-interactive mode.
      The command fails when no fixed or dynamic config exists.
    """
    model_path_match = MODEL_PATH_RE.match(model)
    if model_revision is not None and model_path_match is not None and model_path_match.group(3) is not None:
        raise ValueError(
            "Do not pass --model-revision when --model already includes a revision. "
            "Specify the revision only in the fully qualified --model path."
        )
    inline_placement_value = placement.to_json()
    if placement_id and inline_placement_value is not None:
        raise ValueError("Use either --placement or inline placement options, not both.")

    if merge and attach_adapter:
        raise ValueError("Use either --merge or --attach-adapter, not both.")

    adapter_model = await load_adapter_model(config, model)
    if adapter_model is None and (merge or attach_adapter):
        flag = "--merge" if merge else "--attach-adapter"
        raise ValueError(f"{flag} only applies to LoRA adapter models, and {model} is not an adapter.")
    if adapter_model is not None and not (merge or attach_adapter):
        raise ValueError(
            f"{model} is a LoRA adapter.\n\nChoose how to deploy it:\n"
            "  --attach-adapter*  Attach the adapter to a deployment for serving multiple LoRA adapters\n"
            "  --merge            Create a new deployment with the adapter merged into its base model"
        )

    # --merge deploys an adapter like any other model; the API merges it into its base model.
    if adapter_model is not None and attach_adapter:
        adapter_revision = model_path_match.group(3) if model_path_match is not None else None
        await _deploy_adapter(
            config,
            adapter=adapter_model,
            adapter_revision=adapter_revision or model_revision,
            endpoint_name_or_id=endpoint_name_or_id,
            config_id=config_id,
            min_replicas=min_replicas,
            max_replicas=max_replicas,
            scale_up_window=scale_up_window,
            scale_down_window=scale_down_window,
            scaling_metric=scaling_metric,
            scaling_target=scaling_target,
            scaling_percentile=scaling_percentile,
            deployment_name=deployment_name,
            placement_id=placement_id,
            placement_value=inline_placement_value if not placement_id else PlacementProfile(profile=placement_id),
            inactive_timeout=inactive_timeout,
            traffic_weight=traffic_weight,
        )
        return

    resolved = await resolve_model_and_config(config, model, config_id=config_id)
    resolved_model, config_value = resolved.model, resolved.config
    # Prefer revision pin from a fully-qualified model path; fall back to the
    # deprecated --model-revision flag.
    resolved_revision = resolved.revision_id or model_revision

    autoscaling = build_autoscaling(
        min_replicas=min_replicas,
        max_replicas=max_replicas,
        scale_up_window=scale_up_window,
        scale_down_window=scale_down_window,
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
        placement_value = inline_placement_value

    model_path = construct_model_path(resolved_model, resolved_revision)

    if not config.json:
        min_replicas_value = int(autoscaling.get("min_replicas") or 1)
        max_replicas_value = int(autoscaling.get("max_replicas") or min_replicas_value)
        hardware_pricing = await show_loading_status(
            "Looking up GPU pricing...",
            resolve_hardware_pricing(
                config,
                config_value,
                min_replicas=min_replicas_value,
                max_replicas=max_replicas_value,
            ),
        )
        _print_deployment_preview(
            endpoint=endpoint_name_or_id,
            deployment_name=deployment_name,
            model=resolved_model,
            model_path=model_path,
            config_value=config_value,
            autoscaling=autoscaling,
            placement=placement_value,
            inactive_timeout=inactive_timeout,
            traffic_weight=traffic_weight,
            hardware_pricing=hardware_pricing,
        )
    await assert_explicit_project_id(config)

    endpoint, is_new_endpoint = await _find_or_create_endpoint(config, endpoint_name_or_id)

    try:
        deployment = await show_loading_status(
            "Creating beta endpoint deployment...",
            config.client.beta.endpoints.deployments.create(
                endpoint.id,
                name=deployment_name,
                model=model_path,
                config=construct_config_path(config_value),
                autoscaling=autoscaling,
                inactive_timeout=inactive_timeout if inactive_timeout is not None else omit,
                # Revision is already embedded in model_path when present.
                model_revision_id=omit,
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


async def _deploy_adapter(
    config: CLIConfigParameter,
    *,
    adapter: Model,
    adapter_revision: str | None,
    endpoint_name_or_id: str,
    config_id: str | None,
    min_replicas: int | None,
    max_replicas: int | None,
    scale_up_window: str | None,
    scale_down_window: str | None,
    scaling_metric: ScalingMetricName | None,
    scaling_target: float | None,
    scaling_percentile: ScalingPercentile | None,
    deployment_name: str | None,
    placement_id: str | None,
    placement_value: Placement | None,
    inactive_timeout: int | None,
    traffic_weight: float | None,
) -> None:
    autoscaling = build_autoscaling(
        min_replicas=min_replicas,
        max_replicas=max_replicas,
        scale_up_window=scale_up_window,
        scale_down_window=scale_down_window,
        scaling_metrics=build_scaling_metrics(
            scaling_metric=scaling_metric,
            scaling_target=scaling_target,
            scaling_percentile=scaling_percentile,
        ),
        required=True,
    )
    base = await show_loading_status("Loading adapter base model...", load_base_model(config, adapter))
    configs = await show_loading_status(
        "Loading base model configs...",
        list_model_configs(config, base.id),
    )
    endpoint = await _peek_endpoint(config, endpoint_name_or_id)
    existing = None
    if endpoint is not None:
        existing = await show_loading_status(
            "Checking endpoint deployments...",
            find_compatible_deployment(
                config,
                endpoint.id,
                base=base,
                configs=configs,
                config_id=config_id,
                deployment_name=deployment_name,
            ),
        )

    config_value = (
        None
        if existing is not None
        else await select_lora_config_for_deploy(config, configs, config_id, model=base.name or base.id)
    )
    if existing is None and deployment_name is None:
        short_uuid = str(uuid.uuid4())[:8]
        deployment_name = f"{base.name}-{short_uuid}".replace("/", "-")

    adapter_label = f"{adapter.name} ({construct_model_path(adapter, adapter_revision)})"
    if not config.json:
        hardware_pricing = None
        if existing is None and config_value is not None:
            min_replicas_value = int(autoscaling.get("min_replicas") or 1)
            max_replicas_value = int(autoscaling.get("max_replicas") or min_replicas_value)
            hardware_pricing = await show_loading_status(
                "Looking up GPU pricing...",
                resolve_hardware_pricing(
                    config,
                    config_value,
                    min_replicas=min_replicas_value,
                    max_replicas=max_replicas_value,
                ),
            )
        preview_name = existing.name if existing is not None else deployment_name
        assert preview_name is not None
        _print_deployment_preview(
            endpoint=endpoint_name_or_id,
            deployment_name=preview_name,
            model=base,
            model_path=construct_model_path(base),
            config_value=config_value,
            config_label=existing.config_id if existing is not None else None,
            adapter_label=adapter_label,
            autoscaling=autoscaling if existing is None else {},
            placement=None if existing is not None else placement_value,
            inactive_timeout=None if existing is not None else inactive_timeout,
            traffic_weight=traffic_weight,
            hardware_pricing=hardware_pricing,
        )
        if existing is not None:
            console.print("[dim]Attaching the adapter to the existing deployment.[/dim]\n")
            if _adapter_create_flags_ignored(
                min_replicas=min_replicas,
                max_replicas=max_replicas,
                scale_up_window=scale_up_window,
                scale_down_window=scale_down_window,
                scaling_metric=scaling_metric,
                scaling_target=scaling_target,
                scaling_percentile=scaling_percentile,
                placement_id=placement_id,
                placement_value=placement_value,
                inactive_timeout=inactive_timeout,
            ):
                console.print(
                    "[yellow]Replica, placement, and timeout flags apply only when a new deployment is created.[/yellow]\n"
                )
        else:
            console.print(
                "[dim]No compatible deployment found. Creating a base-model deployment, then attaching the adapter.[/dim]\n"
            )

    await assert_explicit_project_id(config)

    is_new_endpoint = False
    if endpoint is None:
        endpoint, is_new_endpoint = await _find_or_create_endpoint(config, endpoint_name_or_id)
        if not is_new_endpoint:
            existing = await find_compatible_deployment(
                config,
                endpoint.id,
                base=base,
                configs=configs,
                config_id=config_id,
                deployment_name=deployment_name,
            )

    created_deployment = False
    if existing is None:
        assert config_value is not None
        assert deployment_name is not None
        try:
            deployment = await show_loading_status(
                "Creating beta endpoint deployment...",
                config.client.beta.endpoints.deployments.create(
                    endpoint.id,
                    name=deployment_name,
                    model=construct_model_path(base),
                    config=construct_config_path(config_value),
                    autoscaling=autoscaling,
                    inactive_timeout=inactive_timeout if inactive_timeout is not None else omit,
                    model_revision_id=omit,
                    placement=placement_value or omit,
                ),
            )
            created_deployment = True
        except Exception as e:
            if is_new_endpoint:
                await config.client.beta.endpoints.delete(endpoint.id)
                console.print("Error creating deployment. Rolling back.")
            raise e
    else:
        deployment = existing

    try:
        attached = await show_loading_status(
            "Attaching adapter...",
            config.client.beta.endpoints.adapters.create(
                endpoint_id=endpoint.id,
                deployment_id=deployment.id,
                adapter_model_id=adapter.id,
                adapter_revision_id=adapter_revision if adapter_revision is not None else omit,
            ),
        )
    except Exception as e:
        if created_deployment or is_new_endpoint:
            console.print("Error attaching adapter. Rolling back.")
        if created_deployment:
            await config.client.beta.endpoints.deployments.delete(
                deployment.id,
                endpoint_id=endpoint.id,
                etag=deployment.etag or omit,
            )
        if is_new_endpoint:
            await config.client.beta.endpoints.delete(endpoint.id)
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
        payload: dict[str, Any] = {"endpoint": endpoint, "deployment": deployment, "adapter": attached}
        console.print_json(openapi_dumps(payload).decode("utf-8"))
        return

    console.print(
        f"\n[green]√[/green] Adapter {adapter.name} attached to deployment {deployment.name} on endpoint {endpoint.name}.\n\n"
    )
    await retrieve(endpoint.id, config=config)


def _adapter_create_flags_ignored(
    *,
    min_replicas: int | None,
    max_replicas: int | None,
    scale_up_window: str | None,
    scale_down_window: str | None,
    scaling_metric: ScalingMetricName | None,
    scaling_target: float | None,
    scaling_percentile: ScalingPercentile | None,
    placement_id: str | None,
    placement_value: Placement | None,
    inactive_timeout: int | None,
) -> bool:
    return any(
        (
            min_replicas is not None,
            max_replicas is not None,
            scale_up_window is not None,
            scale_down_window is not None,
            scaling_metric is not None,
            scaling_target is not None,
            scaling_percentile is not None,
            placement_id is not None,
            placement_value is not None,
            inactive_timeout is not None,
        )
    )


async def _peek_endpoint(config: CLIConfigParameter, endpoint_input: str) -> Endpoint | None:
    if endpoint_input.startswith("ep_"):
        return await config.client.beta.endpoints.retrieve(id=endpoint_input)
    try:
        return await resolve_endpoint(config, endpoint_input)
    except ValueError:
        return None


def _print_deployment_preview(
    *,
    endpoint: str,
    deployment_name: str,
    model: Model,
    model_path: str,
    config_value: Config | None,
    autoscaling: DeploymentAutoscalingParam,
    placement: Placement | None,
    inactive_timeout: int | None,
    traffic_weight: float | None,
    hardware_pricing: HardwarePricing | None = None,
    adapter_label: str | None = None,
    config_label: str | None = None,
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
    if metrics := autoscaling.get("scaling_metrics"):
        metric = next(iter(metrics))
        add_row("--scaling-metric", metric["name"])
        add_row("--scaling-target", str(metric["target"]))
        if percentile := metric.get("percentile"):
            add_row("--scaling-percentile", percentile)

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
            if (compliance_policy := inline.get("compliance_policy")) and (
                hipaa := compliance_policy.get("hipaa")
            ) is not None:
                add_row("--placement.hipaa", "true" if hipaa else "false")

    if inactive_timeout is not None:
        add_row("--inactive-timeout", str(inactive_timeout))
    if traffic_weight is not None:
        add_row("--traffic-weight", str(traffic_weight))
    add_row("--model", f"{model.name} ({model_path})")
    if adapter_label is not None:
        add_row("--adapter", adapter_label)
    shown_config = config_value.id if config_value is not None and config_value.id else config_label
    if shown_config:
        add_row("--config", shown_config)

    table.add_row("\n".join(args))

    console.print(
        Panel(
            table,
            title="Deploy [bold][primary]preview[/primary][/bold]",
            title_align="left",
        )
    )

    if hardware_pricing is not None:
        console.print(
            f"[dim][/dim][yellow]This deployment will utilize {hardware_pricing.gpu_label}, "
            f"which is estimated to cost approximately {hardware_pricing.estimated_price_label}.[/yellow]\n"
        )


# Helper method to enable the users to use this command to either create a new endpoint+deployment
# or append a new deployment to an existing endpoint
async def _find_or_create_endpoint(config: CLIConfigParameter, endpoint_input: str) -> tuple[Endpoint, bool]:
    # If the user gave us an endpoint ID, we can just retrieve it.
    if endpoint_input.startswith("ep_"):
        endpoint = await config.client.beta.endpoints.retrieve(id=endpoint_input)
        return endpoint, False

    # Create first; on name conflict, reuse the existing endpoint.
    try:
        endpoint = await config.client.beta.endpoints.create(name=endpoint_input)
        return endpoint, True
    except ConflictError:
        return await resolve_endpoint(config, endpoint_input), False
