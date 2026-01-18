import click

from together import Together
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.argument("endpoint-id", required=True)
@click.option("--wait/--no-wait", default=True, help="Wait for the endpoint to start")
@click.pass_obj
@handle_api_errors("Endpoints")
def start(client: Together, endpoint_id: str, wait: bool) -> None:
    """Start a dedicated inference endpoint."""
    client.endpoints.update(endpoint_id, state="STARTED")
    click.echo("Successfully marked endpoint as starting", err=True)

    if wait:
        import time

        click.echo("Waiting for endpoint to start...", err=True)
        while client.endpoints.retrieve(endpoint_id).state != "STARTED":
            time.sleep(1)
        click.echo("Endpoint started", err=True)

    click.echo(endpoint_id)
