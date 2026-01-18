import click

from together import Together
from together.lib.cli.api._utils import handle_api_errors
from together.lib.utils.serializer import datetime_serializer


@click.command()
@click.argument("endpoint-id", required=True)
@click.option("--json", is_flag=True, help="Print output in JSON format")
@click.pass_context
@handle_api_errors("Endpoints")
def retrieve(ctx: click.Context, endpoint_id: str, json: bool) -> None:
    """Get a dedicated inference endpoint."""
    client: Together = ctx.obj

    endpoint = client.endpoints.retrieve(endpoint_id)
    if json:
        import json as json_lib

        click.echo(json_lib.dumps(endpoint.model_dump(), indent=2, default=datetime_serializer))
    else:
        ctx.obj.print_endpoint(endpoint)
