import click

from together import Together
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.option("--json", is_flag=True, help="Print output in JSON format")
@click.pass_obj
@handle_api_errors("Endpoints")
def availability_zones(client: Together, json: bool) -> None:
    """List all availability zones."""
    avzones = client.endpoints.list_avzones()

    if not avzones:
        click.echo("No availability zones found", err=True)
        return

    if json:
        import json as json_lib

        click.echo(json_lib.dumps(avzones.model_dump(), indent=2))
    else:
        click.echo("Available zones:", err=True)
        for availability_zone in sorted(avzones.avzones):
            click.echo(f"  {availability_zone}")
