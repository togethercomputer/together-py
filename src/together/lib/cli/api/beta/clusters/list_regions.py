from __future__ import annotations

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable


async def list_regions(
    *,
    config: CLIConfigParameter,
) -> None:
    """List regions."""
    response = await config.client.beta.clusters.list_regions()

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    table = ListTable()
    table.add_primary_column("ID")
    table.add_column("Region")
    table.add_column("GPU Options")
    table.add_column("NVIDIA Driver")
    table.add_column("CUDA Version")
    table.add_column("OS")
    for region in response.regions:
        gpu_options = "\n".join(region.supported_instance_types or [])
        for driver_version in region.driver_versions:
            table.add_row(
                f"[blue]{driver_version.id}[/blue]",
                region.name,
                gpu_options,
                driver_version.nvidia_driver_version,
                driver_version.cuda_version,
                driver_version.os,
            )

    console.print(table)
