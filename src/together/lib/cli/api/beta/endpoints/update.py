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
from together.lib.cli.api.beta.endpoints.retrieve import retrieve as retrieve_endpoint
from together.lib.cli.api.beta.endpoints._utils._traffic_split import upsert_traffic_weight
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
    name: Annotated[Optional[str], Parameter(help="Updated deployment name")] = None,
    min_replicas: Annotated[
        Optional[int], Parameter(help="New minimum replicas; set both replica bounds to 0 to stop the deployment")
    ] = None,
    max_replicas: Annotated[
        Optional[int], Parameter(help="New maximum replicas; must be greater than or equal to --min-replicas")
    ] = None,
    scale_up_window: Annotated[
        Optional[str],
        Parameter(help="Seconds the metric must stay above target before adding replicas (for example, 30s)"),
    ] = None,
    scale_down_window: Annotated[
        Optional[str],
        Parameter(help="Cooldown in seconds before removing more replicas after scale-down (for example, 60s)"),
    ] = None,
    scale_to_zero_window: Annotated[
        Optional[str],
        Parameter(help="Idle time in seconds before scaling to zero replicas (for example, 300s)"),
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
    etag: Annotated[Optional[str], Parameter(help="ETag for optimistic concurrency")] = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """Update a deployment's parameters on an endpoint."""

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
        required=False,
    )

    update_mask: list[str] = []
    kwargs: dict[str, Any] = {}

    if name is not None:
        kwargs["name"] = name
        update_mask.append("name")
    if autoscaling is not None:
        kwargs["autoscaling"] = autoscaling
        update_mask.append("autoscaling")
    if etag is not None:
        kwargs["etag"] = etag

    if not update_mask and traffic_weight is None:
        console.print("Error: At least one update option must be specified.")
        sys.exit(1)

    endpoint = await find_endpoint_by_deployment(config.client, id)

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

    if config.json:
        if updated is not None:
            console.print_json(openapi_dumps(updated).decode("utf-8"))
        else:
            console.print_json(openapi_dumps(endpoint).decode("utf-8"))
        return

    if updated is not None:
        console.print(f"[green]√[/green] Updated deployment {updated.name or id}.\n\n")
    else:
        console.print(f"[green]√[/green] Updated traffic weight for deployment {id}.\n\n")
    await retrieve_endpoint(endpoint.id, config=config)
