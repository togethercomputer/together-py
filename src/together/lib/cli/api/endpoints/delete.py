import click

from together import Together
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.argument("endpoint-id", required=True)
@click.pass_obj
@handle_api_errors("Endpoints")
def delete(client: Together, endpoint_id: str) -> None:
    """Delete a dedicated inference endpoint."""
    client.endpoints.delete(endpoint_id)
    click.echo("Successfully deleted endpoint", err=True)
    click.echo(endpoint_id)
