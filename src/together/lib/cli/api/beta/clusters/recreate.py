from __future__ import annotations

import httpx

from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.clusters._util import print_clusters


async def recreate(
    cluster_id: str,
    *,
    reason: str | None = None,
    config: CLIConfigParameter,
) -> None:
    """Tear down and rebuild a cluster while preserving its reservation."""

    body = {"reason": reason} if reason else {}

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
    resp = input(f"Clusters: Are you sure you want to recreate cluster {cluster.cluster_name}? [y/N] ").strip().lower()
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
