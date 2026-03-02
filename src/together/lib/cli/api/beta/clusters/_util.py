from typing import List

from together.types.beta.cluster import Cluster
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable


def print_clusters(clusters: List[Cluster]) -> None:
    table = ListTable()
    table.add_column("ID")
    table.add_primary_column("Name")
    table.add_column("Status")
    table.add_column("Region")
    for cluster in clusters:
        table.add_row(cluster.cluster_id, cluster.cluster_name, cluster.status, cluster.region)
    console.print(table)
