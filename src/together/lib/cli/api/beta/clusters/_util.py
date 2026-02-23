from typing import List

from together.types.beta.cluster import Cluster
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable


def print_clusters(clusters: List[Cluster]) -> None:
    table = ListTable()
    table.add_column("ID", ratio=2)
    table.add_primary_column("Name", ratio=2)
    table.add_column("Status")
    table.add_column("Region")
    for cluster in clusters:
        status_color = status_colors[cluster.status] if cluster.status in status_colors else "white"

        table.add_row(
            f"[link=https://api.together.xyz/clusters/id/{cluster.cluster_id}]{cluster.cluster_id}[/link]",
            cluster.cluster_name,
            f"[{status_color}]{cluster.status}[/{status_color}]",
            cluster.region,
        )
    console.print(table)


status_colors = {
    "WaitingForControlPlaneNodes": "yellow",
    "WaitingForDataPlaneNodes": "yellow",
    "WaitingForSubnet": "yellow",
    "WaitingForSharedVolume": "yellow",
    "InstallingDrivers": "yellow",
    "RunningAcceptanceTests": "yellow",
    "Paused": "yellow",
    "OnDemandComputePaused": "yellow",
    "Scheduled": "yellow",
    "Ready": "green",
    "Degraded": "red",
    "Deleting": "red",
}
