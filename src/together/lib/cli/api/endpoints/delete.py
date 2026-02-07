import json as json_lib

import click

from together import Together
from together.lib.cli.api._utils import handle_api_errors
from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors


@click.command()
@click.argument("endpoint-id", required=True)
@click.option("--json", is_flag=True, help="Print output in JSON format")
@click.pass_obj
@handle_api_errors("Endpoints")
@handle_endpoint_api_errors("Endpoints")
def delete(client: Together, endpoint_id: str, json: bool) -> None:
    """Delete a dedicated inference endpoint."""
    client.endpoints.delete(endpoint_id)
    if json:
        click.echo(json_lib.dumps({"message": "Successfully deleted endpoint"}, indent=2))
        return

    click.echo("Successfully deleted endpoint", err=True)
    click.echo(endpoint_id)
