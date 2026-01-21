import json as json_lib
from typing import Any, Dict, List, Optional

import click
from tabulate import tabulate

from together import Together, omit
from together._response import APIResponse as APIResponse
from together.lib.cli.api._utils import handle_api_errors
from together.lib.utils.serializer import datetime_serializer


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

    if json:
        items = [model.model_dump() for model in models_list]
        click.echo(json_lib.dumps(items, indent=2, default=datetime_serializer))
        return

    display_list: List[Dict[str, Any]] = []
    for model in sorted(models_list, key=lambda x: x.type):
        price_parts: List[str] = []

        # Only show pricing if a value actually exists
        if model.pricing and model.pricing.input > 0 and model.pricing.output > 0:
            price_parts.append(f"${model.pricing.input:.2f}")
            price_parts.append(f"${model.pricing.output:.2f}")

        display_list.append(
            {
                "Model": model.id,
                "Type": model.type,
                "Context length": model.context_length if model.context_length else None,
                "Price per 1M Tokens (input/output)": "/".join(price_parts),
            }
        )

    click.echo(tabulate(display_list, headers="keys"))
