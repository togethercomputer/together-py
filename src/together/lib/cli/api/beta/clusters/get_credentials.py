from __future__ import annotations

import errno
import os
import stat
import sys
from pathlib import Path
from typing import Annotated, Any, Optional

from cyclopts import Parameter

from together import AsyncTogether, TogetherError



async def get_credentials(
    cluster_id: str,
    file: Optional[str] = None,
    context_name: Optional[str] = None,
    overwrite_existing: bool = False,
    set_default_context: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Get cluster credentials."""
    import base64
    import platform

    if file is None:
        file = os.path.join(os.path.expanduser("~"), ".kube", "config")
    cluster = await client.beta.clusters.retrieve(cluster_id)
    kube_config = base64.b64decode(cluster.kube_config).decode("utf-8")
    if len(kube_config) == 0:
        print("No kubeconfig found for cluster at this time.")
        return
    if file == "-":
        print(kube_config)
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
        print("Together cli dependencies are missing. Please run: pip install together[cli]", file=sys.stderr)
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
            print(
                f"{kube_config_path} has permissions \"{existing_file_perms}\". "
                "It should be readable and writable only by its owner.",
                file=sys.stderr,
            )
            return

    with open(kube_config_path, "w+") as stream:
        stream.write(dump(kube_config_dict))
    print(f"Kubeconfig written to {kube_config_path}")


def _handle_merge(
    existing: dict[str, Any], addition: dict[str, Any], key: str, overwrite_existing: bool
) -> None:
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
