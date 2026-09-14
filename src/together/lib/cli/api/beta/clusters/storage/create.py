from __future__ import annotations

from typing import Optional, Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console


async def create(
    region: Annotated[str, Parameter(help="Region to create the storage volume in")],
    size_tib: Annotated[int, Parameter(help="Size of the storage volume in TiB")],
    volume_name: Annotated[str, Parameter(help="Name of the storage volume")],
    is_lifecycle_independent: Annotated[
        Optional[bool],
        Parameter(help="Keep the storage volume after cluster decommissioning"),
    ] = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """Create a storage volume."""
    response = await config.client.beta.clusters.storage.create(
        region=region,
        size_tib=size_tib,
        volume_name=volume_name,
        is_lifecycle_independent=is_lifecycle_independent if is_lifecycle_independent is not None else omit,
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
    else:
        console.print(f"[blue]Storage volume created successfully[/blue]")
        console.print(f"[primary]Volume ID:[/primary] {response.volume_id}")
