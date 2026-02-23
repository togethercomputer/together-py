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
    table.add_primary_column("Region")
    table.add_primary_column("GPU Options")
    table.add_primary_column("Driver Versions")
    for region in response.regions:
        driver_versions: list[str] = []
        for driver_version in region.driver_versions or []:
            driver_versions.append(
                f"[dim]NVIDIA Driver:[/dim] [blue]{driver_version.nvidia_driver_version}[/blue] [dim]CUDA Version:[/dim] [blue]{driver_version.cuda_version}[/blue]"
            )

        table.add_row(region.name, "\n".join(region.supported_instance_types or []), "\n".join(driver_versions))

    console.print(table)
