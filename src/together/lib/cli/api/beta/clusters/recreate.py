from __future__ import annotations

from typing import Literal

import httpx

from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.clusters._util import print_clusters


async def recreate(
    cluster_id: str,
    *,
    reason: str | None = None,
    cluster_type: Literal["KUBERNETES", "SLURM"] | None = None,
    num_gpus: int | None = None,
    num_reserved_gpus: int | None = None,
    num_capacity_pool_gpus: int | None = None,
    num_preemptible_gpus: int | None = None,
    config: CLIConfigParameter,
) -> None:
    """Tear down and rebuild a cluster while preserving its reservation.

    Spec options (cluster type and GPU count targets) are applied as the
    cluster's new spec; when none are given, the current spec is kept.
    """

    new_spec = {
        key: value
        for key, value in {
            "cluster_type": cluster_type,
            "num_gpus": num_gpus,
            "num_reserved_gpus": num_reserved_gpus,
            "num_capacity_pool_gpus": num_capacity_pool_gpus,
            "num_preemptible_gpus": num_preemptible_gpus,
        }.items()
        if value is not None
    }

    body: dict[str, object] = {}
    if reason:
        body["reason"] = reason
    if new_spec:
        body["new_spec"] = new_spec

    if config.json:
        response = await config.client.post(
            f"/compute/clusters/{cluster_id}:recreate",
            cast_to=httpx.Response,
            body=body,
        )
        console.print_json(response.text)
        return

    cluster = await show_loading_status("", config.client.beta.clusters.retrieve(cluster_id=cluster_id))
    print_clusters([cluster])
    resp = (
        input(f"Clusters: Are you sure you want to recreate cluster {cluster.cluster_name}? [y/N] ").strip().lower()
    )
    if resp != "y" and resp != "yes":
        return
    response = await show_loading_status(
        "Recreating cluster...",
        config.client.post(f"/compute/clusters/{cluster_id}:recreate", cast_to=httpx.Response, body=body),
    )
    intent = response.json()
    console.print(
        f"Recreate requested for {cluster.cluster_name} ({cluster_id}); intent {intent.get('id')} is {intent.get('status')}"
    )
