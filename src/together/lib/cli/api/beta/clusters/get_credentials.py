from __future__ import annotations
import click
import os
from pathlib import Path
from together import Together
from together.lib.cli.api._utils import handle_api_errors

@click.command()
@click.argument("cluster-id", required=True)
@click.option(
    "--file",
    default=os.path.expanduser("~/.kube/config"),
    show_default=True,
    type=str,
    help="Path to write the kubeconfig to",
)
@click.pass_context
@handle_api_errors("Clusters")
def get_credentials(ctx: click.Context, cluster_id: str, file: str) -> None:
    """Get cluster credentials"""
    client: Together = ctx.obj

    cluster = client.beta.clusters.retrieve(cluster_id)

    import base64

    kube_config_decoded = base64.b64decode(cluster.kube_config).decode("utf-8")
    kube_config_path = Path(os.path.expanduser(file if file else "~/.kube/config"))

    if file == "-":
        click.echo(kube_config_decoded)
        return

    # Write the decoded kubeconfig to the user's default kubeconfig path
    # Ensure the .kube directory exists before writing the config file
    kube_dir = kube_config_path.parent
    # Only create directory if it's not the current directory (which happens when filename has no path component)
    if kube_dir != Path(".") and not kube_dir.exists():
        kube_dir.mkdir(parents=True, exist_ok=True)
    with open(kube_config_path, "w") as f:
        f.write(kube_config_decoded)
    click.secho(f"Kubeconfig written to {kube_config_path}", fg="green")