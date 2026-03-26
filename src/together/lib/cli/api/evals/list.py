from typing import Any, Dict, List, Union, Literal

import click
from rich import print_json
from tabulate import tabulate

from together import Together, omit
from together._utils._json import openapi_dumps
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.option(
    "--status",
    type=click.Choice(["pending", "queued", "running", "completed", "error", "user_error"]),
    help="Filter by job status.",
)
@click.option(
    "--limit",
    type=int,
    help="Limit number of results (max 100).",
)
@click.option("--json", is_flag=True, help="Print output in JSON format")
@click.pass_context
@handle_api_errors("Evals")
def list(
    ctx: click.Context,
    status: Union[Literal["pending", "queued", "running", "completed", "error", "user_error"], None],
    limit: Union[int, None],
    json: bool,
) -> None:
    """List evals"""

    client: Together = ctx.obj

    response = client.evals.list(status=status or omit, limit=limit or omit)

    if json:
        print_json(openapi_dumps(response).decode("utf-8"))
        return

    display_list: List[Dict[str, Any]] = []
    for job in response:
        if job.parameters:
            model = job.parameters.get("model_to_evaluate", "")
            model_a = job.parameters.get("model_a", "")
            model_b = job.parameters.get("model_b", "")
        else:
            model = ""
            model_a = ""
            model_b = ""

        display_list.append(
            {
                "Workflow ID": job.workflow_id or "",
                "Type": job.type,
                "Status": job.status,
                "Created At": job.created_at or 0,
                "Model": model,
                "Model A": model_a,
                "Model B": model_b,
            }
        )

    table = tabulate(display_list, headers="keys", tablefmt="grid", showindex=True)
    click.echo(table)
