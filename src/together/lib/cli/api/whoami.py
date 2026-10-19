from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._whoami import project_of, organization_of
from together.lib.cli.utils._console import console


async def whoami(*, config: CLIConfigParameter) -> None:
    me = await config.client.whoami()

    if config.json:
        console.print_json(openapi_dumps(me).decode("utf-8"))
        return

    user = getattr(me, "user", None)
    api_key = getattr(me, "api_key", None)
    project = project_of(me)
    organization = organization_of(me)

    if user is not None:
        console.print(f"        User: [bold]{user.id}[/bold]")
    if api_key is not None:
        console.print(f"     API key: [bold]{api_key.id}[/bold]")
    if project is not None:
        console.print(f"     Project: [bold]{project.name}[/bold] [dim]({project.id})[/dim]")
    if organization is not None:
        console.print(f"Organization: [bold]{organization.name}[/bold] [dim]({organization.id})[/dim]")
