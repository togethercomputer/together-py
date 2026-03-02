from typing import List

from tabulate import tabulate

from together.types.beta.cluster import Cluster

def print_clusters(clusters: List[Cluster]) -> None:
    import sys

    data = []
    for cluster in clusters:
        data.append(
            {
                "ID": cluster.cluster_id,
                "Name": cluster.cluster_name,
                "Status": cluster.status,
                "Region": cluster.region,
            }
        )
    print(tabulate(data, headers="keys", tablefmt="grid"), file=sys.stderr)
