from __future__ import annotations

import os
import stat
import errno
import platform
from typing import Any
from pathlib import Path

import click

from together import Together, TogetherError
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.argument("cluster-id", required=True)
@click.option(
    "--file",
    default=os.path.join(os.path.expanduser("~"), ".kube", "config"),
    show_default=True,
    type=str,
    help="Path to write the kubeconfig to. If you pass `-` it will print the config to stdout instead of writing to a file.",
)
@click.option(
    "--context-name",
    type=str,
    help="Name of the context to add to the kubeconfig. By default it will be the cluster name.",
)
@click.option(
    "--overwrite-existing",
    is_flag=True,
    help="If there is a conflict with the existing kubeconfig, overwrite the existing kubeconfig instead of raising an error.",
)
@click.option(
    "--set-default-context",
    is_flag=True,
    help="Change the current context for kubectl to the new context.",
)
@click.pass_context
@handle_api_errors("Clusters")
def get_credentials(
    ctx: click.Context,
    cluster_id: str,
    file: str,
    context_name: str | None = None,
    overwrite_existing: bool = False,
    set_default_context: bool = False,
) -> None:
    """Get cluster credentials"""
    client: Together = ctx.obj

    cluster = client.beta.clusters.retrieve(cluster_id)

    import base64

    kube_config = base64.b64decode(cluster.kube_config).decode("utf-8")

    if len(kube_config) == 0:
        click.echo("No kubeconfig found for cluster at this time.")
        return

    if file == "-":
        click.echo(kube_config)
        return

    kube_config_path = Path(os.path.expanduser(file if file else "~/.kube/config"))

    # ensure that at least an empty ~/.kube/config exists
    directory = os.path.dirname(kube_config_path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                raise
    if not os.path.exists(kube_config_path):
        with os.fdopen(os.open(kube_config_path, os.O_CREAT | os.O_WRONLY, 0o600), "wt"):
            pass

    # Write the decoded kubeconfig to the user's default kubeconfig path
    # Ensure the .kube directory exists before writing the config file
    try:
        from yaml import dump, safe_load
    except ImportError:
        click.secho("Together cli dependencies are missing. Please run one of the following commands:\n", fg="red")
        click.secho("uv:  uv add together --optional cli", fg="yellow")
        click.secho("pip: pip install together[cli]", fg="yellow")
        return

    # Load both configs into dictionaries to merge them
    kube_config_dict: dict[str, Any] | None = safe_load(kube_config_path.read_text())
    incoming_config_dict: dict[str, Any] = safe_load(kube_config)

    # If the user did not pass a custom context name, we will use the cluster name
    if context_name is None:
        context_name = cluster.cluster_name

    # Update the context name on the incoming data.
    incoming_config_dict["contexts"][0]["name"] = context_name
    incoming_config_dict["contexts"][0]["context"]["cluster"] = context_name
    incoming_config_dict["clusters"][0]["name"] = context_name

    # If there is not a current kube config on disk, we can safely just take the incoming config
    if kube_config_dict is None:
        kube_config_dict = incoming_config_dict
    else:
        _handle_merge(kube_config_dict, incoming_config_dict, "clusters", overwrite_existing)
        _handle_merge(kube_config_dict, incoming_config_dict, "users", overwrite_existing)
        _handle_merge(kube_config_dict, incoming_config_dict, "contexts", overwrite_existing)

    # Set the current context to the new context if the user requested it.
    if set_default_context:
        kube_config_dict["current-context"] = context_name

    # check that ~/.kube/config is only read- and writable by its owner
    if platform.system() != "Windows" and not os.path.islink(kube_config_path):
        existing_file_perms = "{:o}".format(stat.S_IMODE(os.lstat(kube_config_path).st_mode))
        if not existing_file_perms.endswith("600"):
            click.echo(
                f'{kube_config_path} has permissions "{existing_file_perms}".\nIt should be readable and writable only by its owner.',
            )
            return

    with open(kube_config_path, "w+") as stream:
        stream.write(dump(kube_config_dict))

    click.secho(f"Kubeconfig written to {kube_config_path}", fg="green")


def _handle_merge(existing: dict[str, Any], addition: dict[str, Any], key: str, overwrite_existing: bool) -> None:
    """Merge the incoming kube config into the existing config for the given key."""
    if not addition.get(key, False):
        return
    if not existing.get(key):
        existing[key] = addition[key]
        return

    for i in addition[key]:
        for j in existing[key]:
            if not i.get("name", False) or not j.get("name", False):
                continue
            if i["name"] == j["name"]:
                if overwrite_existing or i == j:
                    existing[key].remove(j)
                    break
                else:
                    raise TogetherError(
                        f"A different object named {i['name']} already exists in {key} in your kubeconfig file."
                    )
        existing[key].append(i)
