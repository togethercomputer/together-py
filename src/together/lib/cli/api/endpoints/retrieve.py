import click
from rich import print_json

from together import Together
from together._utils._json import openapi_dumps
from together.lib.cli.api._utils import handle_api_errors
from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors


@click.command()
@click.argument("endpoint-id", required=True)
@click.option("--json", is_flag=True, help="Print output in JSON format")
@click.pass_context
@handle_api_errors("Endpoints")
@handle_endpoint_api_errors("Endpoints")
def retrieve(ctx: click.Context, endpoint_id: str, json: bool) -> None:
    """Get a dedicated inference endpoint."""
    client: Together = ctx.obj

    endpoint = client.endpoints.retrieve(endpoint_id)
    if json:
        print_json(openapi_dumps(endpoint.model_dump()).decode("utf-8"))
    else:
        ctx.obj.print_endpoint(endpoint)
