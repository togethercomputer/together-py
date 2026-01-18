import json as json_lib
from typing import Any, Dict, List, Optional

import click
from tabulate import tabulate

from together import Together, omit
from together._models import BaseModel
from together._response import APIResponse as APIResponse
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.option(
    "--type",
    type=click.Choice(["dedicated"]),
    help="Filter models by type (dedicated: models that can be deployed as dedicated endpoints)",
)
@click.option(
    "--json",
    is_flag=True,
    help="Output in JSON format",
)
@click.pass_context
@handle_api_errors("Models")
def list(ctx: click.Context, type: Optional[str], json: bool) -> None:
    """List models"""
    client: Together = ctx.obj

    models_list = client.models.list(dedicated=type == "dedicated" if type else omit)

    display_list: List[Dict[str, Any]] = []
    model: BaseModel
    for model in models_list:
        display_list.append(
            {
                "ID": model.id,
                "Name": model.display_name,
                "Organization": model.organization,
                "Type": model.type,
                "Context Length": model.context_length,
                "License": model.license,
                "Input per 1M token": model.pricing.input if model.pricing else None,
                "Output per 1M token": model.pricing.output if model.pricing else None,
            }
        )

    if json:
        click.echo(json_lib.dumps(display_list, indent=2))
    else:
        click.echo(tabulate(display_list, headers="keys", tablefmt="plain"))
