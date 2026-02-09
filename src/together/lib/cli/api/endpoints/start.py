import json as json_lib

import click

from together import Together
from together.lib.cli.api._utils import handle_api_errors
from together.lib.utils.serializer import datetime_serializer
from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors


@click.command()
@click.argument("endpoint-id", required=True)
@click.option("--wait", is_flag=True, help="Wait for the endpoint to start")
@click.option("--json", is_flag=True, help="Print output in JSON format")
@click.pass_obj
@handle_api_errors("Endpoints")
@handle_endpoint_api_errors("Endpoints")
def start(client: Together, endpoint_id: str, wait: bool, json: bool) -> None:
    """Start a dedicated inference endpoint."""
    response = client.endpoints.update(endpoint_id, state="STARTED")

    if json:
        click.echo(json_lib.dumps(response.model_dump(), default=datetime_serializer, indent=2))
        return

    click.echo("Successfully marked endpoint as starting", err=True)

    if wait:
        import time

        click.echo("Waiting for endpoint to start...", err=True)
        while client.endpoints.retrieve(endpoint_id).state != "STARTED":
            time.sleep(1)
        click.echo("Endpoint started", err=True)

    click.echo(endpoint_id)
