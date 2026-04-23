from __future__ import annotations

import os
import stat
import errno
from typing import Any, Optional, Annotated
from pathlib import Path

from cyclopts import Parameter

from together import TogetherError
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status


async def get_credentials(
    cluster_id: str,
    file: Annotated[
        Optional[str],
        Parameter(
            allow_leading_hyphen=True,
            show_default=True,
            help="Path to write the kubeconfig to. If you pass `-` it will print the config to stdout instead of writing to a file.",
        ),
    ] = os.path.join(os.path.expanduser("~"), ".kube", "config"),
    context_name: Annotated[
        Optional[str],
        Parameter(help="Name of the context to add to the kubeconfig. By default it will be the cluster name."),
    ] = None,
    overwrite_existing: Annotated[
        bool,
        Parameter(
            help="If there is a conflict with the existing kubeconfig, overwrite the existing kubeconfig instead of raising an error."
        ),
    ] = False,
    set_default_context: Annotated[
        bool, Parameter(help="If true, set the default context to the cluster name.")
    ] = False,
    *,
    config: CLIConfigParameter,
) -> None:
    """Get cluster credentials."""
    import base64
    import platform

    if file is None:
        file = os.path.join(os.path.expanduser("~"), ".kube", "config")

    cluster = await show_loading_status(
        "Loading cluster credentials...", config.client.beta.clusters.retrieve(cluster_id)
    )
    raw_kc = cluster.kube_config
    if not raw_kc:
        kube_config = ""
    else:
        try:
            kube_config = base64.b64decode(raw_kc).decode("utf-8")
        except Exception as e:
            if config.json:
                console.print_json(
                    openapi_dumps(
                        {"kubeconfig": None, "message": f"Could not decode cluster kube_config (base64): {e!s}"}
                    ).decode("utf-8")
                )
            else:
                console.print(f"Could not decode cluster kubeconfig: {e}")
            return
    if len(kube_config) == 0:
        if config.json:
            console.print_json(
                openapi_dumps({"kubeconfig": None, "message": "No kubeconfig found for cluster at this time."}).decode(
                    "utf-8"
                )
            )
        else:
            console.print("No kubeconfig found for cluster at this time.")
        return
    if file == "-":
        if config.json:
            console.print_json(openapi_dumps({"kubeconfig": kube_config}).decode("utf-8"))
        else:
            console.print(kube_config)
        return

    # JSON mode: report the target path only (no merge/write — avoids touching ~/.kube in CI and subprocess tests).
    if config.json:
        try:
            from yaml import safe_load
        except ImportError:
            console.print("Together cli dependencies are missing. Please run: pip install together[cli]")
            return
        incoming_preview: dict[str, Any] | None = safe_load(kube_config)
        if incoming_preview is None:
            console.print_json(
                openapi_dumps({"kubeconfig_path": None, "message": "Cluster kube_config was not valid YAML."}).decode(
                    "utf-8"
                )
            )
            return
        if context_name is None:
            context_name = cluster.cluster_name
        try:
            incoming_preview["contexts"][0]["name"] = context_name
            incoming_preview["contexts"][0]["context"]["cluster"] = context_name
            incoming_preview["clusters"][0]["name"] = context_name
        except (KeyError, IndexError, TypeError) as e:
            console.print_json(
                openapi_dumps(
                    {
                        "kubeconfig_path": str(Path(os.path.expanduser(file))),
                        "message": f"Cluster kube_config YAML was missing expected fields: {e!s}",
                    }
                ).decode("utf-8")
            )
            return
        kube_config_path = Path(os.path.expanduser(file))
        if set_default_context:
            incoming_preview["current-context"] = context_name
        console.print_json(openapi_dumps({"kubeconfig_path": str(kube_config_path)}).decode("utf-8"))
        return

    kube_config_path = Path(os.path.expanduser(file))
    directory = kube_config_path.parent
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                raise
    if not os.path.exists(kube_config_path):
        with os.fdopen(os.open(kube_config_path, os.O_CREAT | os.O_WRONLY, 0o600), "wt"):
            pass

    try:
        from yaml import dump, safe_load
    except ImportError:
        console.print("Together cli dependencies are missing. Please run: pip install together[cli]")
        return

    kube_config_dict: Optional[dict[str, Any]] = safe_load(kube_config_path.read_text())
    incoming_config_dict: dict[str, Any] = safe_load(kube_config)
    if context_name is None:
        context_name = cluster.cluster_name
    incoming_config_dict["contexts"][0]["name"] = context_name
    incoming_config_dict["contexts"][0]["context"]["cluster"] = context_name
    incoming_config_dict["clusters"][0]["name"] = context_name

    if kube_config_dict is None:
        kube_config_dict = incoming_config_dict
    else:
        _handle_merge(kube_config_dict, incoming_config_dict, "clusters", overwrite_existing)
        _handle_merge(kube_config_dict, incoming_config_dict, "users", overwrite_existing)
        _handle_merge(kube_config_dict, incoming_config_dict, "contexts", overwrite_existing)
    if set_default_context:
        kube_config_dict["current-context"] = context_name

    if platform.system() != "Windows" and not os.path.islink(kube_config_path):
        existing_file_perms = "{:o}".format(stat.S_IMODE(os.lstat(kube_config_path).st_mode))
        if not existing_file_perms.endswith("600"):
            console.print(
                f'{kube_config_path} has permissions "{existing_file_perms}". '
                "It should be readable and writable only by its owner.",
            )
            return

    with open(kube_config_path, "w+") as stream:
        stream.write(dump(kube_config_dict))

    console.print(f"Kubeconfig written to {kube_config_path}")


def _handle_merge(existing: dict[str, Any], addition: dict[str, Any], key: str, overwrite_existing: bool) -> None:
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
