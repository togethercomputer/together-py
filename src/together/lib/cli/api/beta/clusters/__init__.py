from typing import Any, Dict, List

import click
from tabulate import tabulate

from together.types.beta.cluster import Cluster

from .list import list
from .create import create
from .delete import delete
from .update import update
from .storage import storage
from .retrieve import retrieve
from .list_regions import list_regions
from .get_credentials import get_credentials


@click.group()
@click.pass_context
def clusters(ctx: click.Context) -> None:
    """Clusters API commands"""

    def _print_clusters(clusters: List[Cluster]) -> None:
        data: List[Dict[str, Any]] = []
        for cluster in clusters:
            data.append(
                {
                    "ID": cluster.cluster_id,
                    "Name": cluster.cluster_name,
                    "Status": cluster.status,
                    "Region": cluster.region,
                }
            )
        click.echo(tabulate(data, headers="keys", tablefmt="grid"))

    ctx.obj.print_clusters = _print_clusters
    pass


clusters.add_command(list)
clusters.add_command(storage)
clusters.add_command(create)
clusters.add_command(retrieve)
clusters.add_command(update)
clusters.add_command(delete)
clusters.add_command(list_regions)
clusters.add_command(get_credentials)
