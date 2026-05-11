from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console


async def update(
    volume_id: str,
    size_tib: Annotated[int, Parameter(help="New size of the storage volume in TiB")],
    *,
    config: CLIConfigParameter,
) -> None:
    """Update a storage volume (resize)."""
    response = await config.client.beta.clusters.storage.update(
        volume_id=volume_id,
        size_tib=size_tib,
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
    else:
        console.print("[blue]Storage volume updated successfully[/blue]")
        console.print(f"[primary]Volume ID:[/primary] {response.volume_id}")
