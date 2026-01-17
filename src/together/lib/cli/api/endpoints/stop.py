import click

from together import Together
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.argument("endpoint-id", required=True)
@click.option("--wait/--no-wait", default=True, help="Wait for the endpoint to stop")
@click.pass_obj
@handle_api_errors("Endpoints")
def stop(client: Together, endpoint_id: str, wait: bool) -> None:
    """Stop a dedicated inference endpoint."""
    client.endpoints.update(endpoint_id, state="STOPPED")
    click.echo("Successfully marked endpoint as stopping", err=True)

    if wait:
        import time

        click.echo("Waiting for endpoint to stop...", err=True)
        while client.endpoints.retrieve(endpoint_id).state != "STOPPED":
            time.sleep(1)
        click.echo("Endpoint stopped", err=True)

    click.echo(endpoint_id)
