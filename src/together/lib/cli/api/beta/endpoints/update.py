from __future__ import annotations

import sys
from typing import Any, Optional
from typing_extensions import Annotated

from cyclopts import Parameter
from cyclopts.validators import Number

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.types.beta.endpoints.ab_experiment import AbExperiment
from together.lib.cli.api.beta.endpoints.retrieve import retrieve as retrieve_endpoint
from together.lib.cli.api.beta.endpoints._utils._traffic_split import upsert_traffic_weight
from together.lib.cli.api.beta.endpoints._utils._ab_experiments import (
    find_ab_for_deployment,
    build_ab_members_with_percent,
)
from together.lib.cli.api.beta.endpoints._utils._build_autoscaling import (
    SCALING_METRIC_NAMES,
    ScalingMetricName,
    ScalingPercentile,
    build_autoscaling,
    build_scaling_metrics,
)
from together.lib.cli.api.beta.endpoints._utils._find_endpoint_by_deployment import find_endpoint_by_deployment


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
    etag: Annotated[
        Optional[str],
        Parameter(
            help="ETag for optimistic concurrency on the deployment update (does not apply to ab_percent or traffic_weight)."
        ),
    ] = None,
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
    if etag is not None:
        kwargs["etag"] = etag

    if not update_mask and traffic_weight is None and ab_percent is None:
        console.print("Error: At least one update option must be specified.")
        sys.exit(1)

    endpoint = await find_endpoint_by_deployment(config.client, id)

    # Validate / compute A/B members before any mutations so failures leave no partial state.
    ab_members = None
    ab_experiment: AbExperiment | None = None
    ab_already_at_percent = False
    if ab_percent is not None:
        ab_experiment = await find_ab_for_deployment(
            config.client,
            endpoint.id,
            id,
        )
        if ab_experiment is None:
            raise ValueError(f"Deployment {id} is not part of an A/B experiment.")

        ab_members = build_ab_members_with_percent(ab_experiment.members, id, ab_percent)
        current = next(m for m in ab_experiment.members if m.deployment_id == id)
        ab_already_at_percent = current.percent == ab_percent

    updated: Any = None
    if update_mask:
        updated = await show_loading_status(
            "Updating deployment...",
            config.client.beta.endpoints.deployments.update(
                id,
                endpoint_id=endpoint.id,
                update_mask=",".join(update_mask),
                **kwargs,
            ),
        )

    if traffic_weight is not None:
        traffic_split = upsert_traffic_weight(
            endpoint.traffic_split,
            deployment_id=id,
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

    updated_ab: AbExperiment | None = None
    if ab_percent is not None:
        assert ab_experiment is not None
        if ab_already_at_percent:
            updated_ab = ab_experiment
        else:
            assert ab_members is not None
            updated_ab = await show_loading_status(
                "Updating A/B experiment...",
                config.client.beta.endpoints.ab_experiments.update(
                    id=ab_experiment.id,
                    endpoint_id=endpoint.id,
                    update_mask="members",
                    members=ab_members,
                    etag=ab_experiment.etag or omit,
                ),
            )

    if config.json:
        # Preserve pre--ab-percent unwrapped precedence for existing flag combos.
        # Only wrap when --ab-percent is involved (may combine with other updates).
        if ab_percent is not None:
            payload: dict[str, Any] = {"ab_experiment": updated_ab}
            if updated is not None:
                payload["deployment"] = updated
            if traffic_weight is not None:
                payload["endpoint"] = endpoint
            console.print_json(openapi_dumps(payload).decode("utf-8"))
        elif updated is not None:
            console.print_json(openapi_dumps(updated).decode("utf-8"))
        else:
            console.print_json(openapi_dumps(endpoint).decode("utf-8"))
        return

    if updated is not None:
        console.print(f"[green]√[/green] Updated deployment {updated.name or id}.\n\n")
    if traffic_weight is not None:
        console.print(f"[green]√[/green] Updated traffic weight for deployment {id}.\n\n")
    if ab_percent is not None:
        if ab_already_at_percent:
            console.print(f"Deployment {id} is already at {ab_percent}%.\n\n")
        else:
            console.print(f"[green]√[/green] Updated A/B percent for deployment {id}.\n\n")
    await retrieve_endpoint(endpoint.id, config=config)
