from __future__ import annotations

from typing import Any, Optional
from typing_extensions import Annotated

from cyclopts import Parameter
from cyclopts.validators import Number

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils._exit import CliDiagnosticExit
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console, error_console
from together.lib.cli.utils._json_mode import exit_with_message
from together.lib.cli.components.loader import show_loading_status
from together.types.endpoints.ab_experiment import AbExperiment
from together.lib.cli.api.endpoints.retrieve import retrieve as retrieve_endpoint
from together.lib.cli.api.endpoints._utils._traffic_split import upsert_traffic_weight
from together.lib.cli.api.endpoints._utils._ab_experiments import (
    find_ab_for_deployment,
    build_ab_members_with_percent,
)
from together.lib.cli.api.endpoints._utils._build_autoscaling import (
    SCALING_METRIC_NAMES,
    ScalingMetricName,
    ScalingPercentile,
    build_autoscaling,
    build_scaling_metrics,
)
from together.lib.cli.api.endpoints._utils._detach_from_experiments import (
    detach_deployment_from_experiments,
)
from together.lib.cli.api.endpoints._utils._find_endpoint_by_deployment import resolve_deployment_id


async def update(
    id: Annotated[
        str,
        Parameter(help=("Deployment ID to update.")),
    ],
    *,
    min_replicas: Annotated[
        Optional[int],
        Parameter(help="New minimum replicas. To stop a deployment, pass both --min-replicas 0 and --max-replicas 0."),
    ] = None,
    max_replicas: Annotated[
        Optional[int],
        Parameter(
            help=(
                "New maximum replicas; must be greater than or equal to --min-replicas. "
                "To stop a deployment, pass both --min-replicas 0 and --max-replicas 0."
            )
        ),
    ] = None,
    scale_up_window: Annotated[
        Optional[str],
        Parameter(help="Seconds the metric must stay above target before adding replicas (for example, 30s)"),
    ] = None,
    scale_down_window: Annotated[
        Optional[str],
        Parameter(help="Cooldown in seconds before removing more replicas after scale-down (for example, 60s)"),
    ] = None,
    scaling_metric: Annotated[
        Optional[ScalingMetricName],
        Parameter(
            help=(f"Autoscaling metric name. Requires --scaling-target. One of: {', '.join(SCALING_METRIC_NAMES)}."),
        ),
    ] = None,
    scaling_target: Annotated[
        Optional[float],
        Parameter(
            help=(
                "Target value for --scaling-metric. Utilization metrics use 0–100; "
                "other metrics use their native units."
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
    traffic_weight: Annotated[
        Optional[float],
        Parameter(
            help=(
                "Relative capacity weight for this deployment in the endpoint's live traffic split. "
                "Preserves other deployment weights; set to 0 to stop live traffic to this deployment."
            ),
            validator=Number(gte=0),
        ),
    ] = None,
    ab_percent: Annotated[
        Optional[int],
        Parameter(
            help=(
                "A/B experiment traffic percentage for this variant deployment. "
                "Takes from or returns percentage to the control only; other variants are unchanged."
            ),
            validator=Number(gte=1, lte=99),
        ),
    ] = None,
    inactive_timeout: Annotated[
        Optional[int],
        Parameter(
            help="Updated inactive timeout in minutes (0 to disable; otherwise 30-1440).",
            validator=Number(gte=0, lte=1440),
        ),
    ] = None,
    max_concurrent_requests_per_replica: Annotated[
        Optional[str],
        Parameter(
            help=(
                "Updated maximum in-flight inference requests per replica. "
                "0 means unlimited when the config limit is 1 or less."
            )
        ),
    ] = None,
    etag: Annotated[
        Optional[str],
        Parameter(
            help="ETag for optimistic concurrency on the deployment update (does not apply to ab_percent, traffic_weight, or detach)."
        ),
    ] = None,
    detach: Annotated[
        bool,
        Parameter(
            name="--detach",
            help=(
                "Detach the deployment from any associated shadow or A/B experiment. "
                "Deletes the experiment when removing this deployment would leave it empty or without a control."
            ),
            negative=(),
            show_default=False,
        ),
    ] = False,
    config: CLIConfigParameter,
) -> None:
    """Update a deployment's parameters on an endpoint."""

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
        required=False,
        infer_replica_defaults=False,
    )

    update_mask: list[str] = []
    kwargs: dict[str, Any] = {}

    if autoscaling is not None:
        kwargs["autoscaling"] = autoscaling
        update_mask.append("autoscaling")
    if inactive_timeout is not None:
        kwargs["inactive_timeout"] = inactive_timeout
        update_mask.append("inactiveTimeout")
    if max_concurrent_requests_per_replica is not None:
        kwargs["max_concurrent_requests_per_replica"] = max_concurrent_requests_per_replica
        update_mask.append("maxConcurrentRequestsPerReplica")
    if etag is not None:
        kwargs["etag"] = etag

    if not update_mask and traffic_weight is None and ab_percent is None and not detach:
        exit_with_message(
            "Error: At least one update option must be specified.",
            diagnostic="At least one endpoint update option must be specified",
        )
    if detach and ab_percent is not None:
        raise ValueError("--detach cannot be combined with --ab-percent.")

    endpoint, deployment_id = await resolve_deployment_id(config.client, id)

    # Validate / compute A/B members before any mutations so failures leave no partial state.
    ab_members = None
    ab_experiment: AbExperiment | None = None
    ab_already_at_percent = False
    if ab_percent is not None:
        ab_experiment = await find_ab_for_deployment(
            config.client,
            endpoint.id,
            deployment_id,
        )
        if ab_experiment is None:
            raise ValueError(f"Deployment {deployment_id} is not part of an A/B experiment.")

        ab_members = build_ab_members_with_percent(ab_experiment.members, deployment_id, ab_percent)
        current = next(m for m in ab_experiment.members if m.deployment_id == deployment_id)
        ab_already_at_percent = current.percent == ab_percent

    # Detach before other mutations. Membership blocks live traffic and rollouts,
    # and the removal is not rolled back if a later update fails.
    actions: list[str] = []
    if detach:
        actions = await detach_deployment_from_experiments(
            config,
            endpoint=endpoint,
            deployment_id=deployment_id,
        )

    updated: Any = None
    updated_ab: AbExperiment | None = None
    try:
        if update_mask:
            updated = await show_loading_status(
                "Updating deployment...",
                config.client.endpoints.deployments.update(
                    deployment_id,
                    endpoint_id=endpoint.id,
                    update_mask=",".join(update_mask),
                    **kwargs,
                ),
            )

        if traffic_weight is not None:
            traffic_split = upsert_traffic_weight(
                endpoint.traffic_split,
                deployment_id=deployment_id,
                weight=traffic_weight,
            )
            endpoint = await show_loading_status(
                "Updating endpoint traffic split...",
                config.client.endpoints.update(
                    endpoint.id,
                    traffic_split=traffic_split,
                    update_mask="trafficSplit",
                    etag=endpoint.etag or omit,
                ),
            )

        if ab_percent is not None:
            assert ab_experiment is not None
            if ab_already_at_percent:
                updated_ab = ab_experiment
            else:
                assert ab_members is not None
                updated_ab = await show_loading_status(
                    "Updating A/B experiment...",
                    config.client.endpoints.ab_experiments.update(
                        id=ab_experiment.id,
                        endpoint_id=endpoint.id,
                        update_mask="members",
                        members=ab_members,
                        etag=ab_experiment.etag or omit,
                    ),
                )
    except Exception as exc:
        _report_failed_update_after_detach(error=exc, actions=actions, config=config)
        raise

    if config.json:
        console.print_json(
            openapi_dumps(
                _update_json_payload(
                    detach=detach,
                    actions=actions,
                    ab_percent=ab_percent,
                    updated=updated,
                    updated_ab=updated_ab,
                    traffic_weight=traffic_weight,
                    endpoint=endpoint,
                )
            ).decode("utf-8")
        )
        return

    if actions:
        console.print(f"[dim]{'; '.join(actions)}[/dim]")
    elif detach:
        console.print(f"Deployment {deployment_id} is not attached to a shadow or A/B experiment.\n\n")
    if updated is not None:
        console.print(f"[green]√[/green] Updated deployment {updated.name or deployment_id}.\n\n")
    if traffic_weight is not None:
        console.print(f"[green]√[/green] Updated traffic weight for deployment {deployment_id}.\n\n")
    if detach and actions and updated is None and traffic_weight is None:
        console.print(f"[green]√[/green] Detached deployment {deployment_id}.\n\n")
    if ab_percent is not None:
        if ab_already_at_percent:
            console.print(f"Deployment {deployment_id} is already at {ab_percent}%.\n\n")
        else:
            console.print(f"[green]√[/green] Updated A/B percent for deployment {deployment_id}.\n\n")
    await retrieve_endpoint(endpoint.id, config=config)


def _update_json_payload(
    *,
    detach: bool,
    actions: list[str],
    ab_percent: int | None,
    updated: Any,
    updated_ab: AbExperiment | None,
    traffic_weight: float | None,
    endpoint: Any,
) -> Any:
    """JSON result for an update.

    Existing flag combos stay unwrapped (a bare deployment, or the endpoint when
    only traffic weight changes). ``--ab-percent`` and ``--detach`` add fields,
    so those results are wrapped.
    """
    if ab_percent is None and not detach:
        if updated is not None:
            return updated
        return endpoint

    payload: dict[str, Any] = {}
    if ab_percent is not None:
        payload["ab_experiment"] = updated_ab
    if updated is not None:
        payload["deployment"] = updated
    if traffic_weight is not None:
        payload["endpoint"] = endpoint
    if detach:
        payload["actions"] = actions
    return payload


def _report_failed_update_after_detach(
    *,
    error: BaseException,
    actions: list[str],
    config: CLIConfigParameter,
) -> None:
    """Surface experiment removals that already committed when a later update fails."""
    if not actions:
        return

    error_message = getattr(error, "message", None) or str(error)
    hint = f"Update failed after irreversible changes: {'; '.join(actions)}"
    if config.json:
        console.print_json(openapi_dumps({"error": error_message, "hint": hint, "actions": actions}).decode("utf-8"))
        # Avoid the outer APIError handler printing a second, action-less JSON error.
        raise CliDiagnosticExit("Update failed after irreversible changes") from error

    error_console.print(f"[yellow]![/yellow] {hint}")
