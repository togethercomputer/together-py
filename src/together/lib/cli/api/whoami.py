from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console


async def whoami(*, config: CLIConfigParameter) -> None:
    me = await config.client.whoami()

    if config.json:
        console.print_json(openapi_dumps(me).decode("utf-8"))
        return

    console.print(f"     Project: [bold]{me.project_name}[/bold] [dim]({me.project_id})[/dim]")
    console.print(f"Organization: [bold]{me.organization_name}[/bold] [dim]({me.organization_id})[/dim]")
