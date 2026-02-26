from typing import List, Optional

import typer
from rich import table as rich_table, print

from together import Together, omit
from together._response import APIResponse as APIResponse
from together._utils._json import openapi_dumps

def list(
    ctx: typer.Context,
    type: Optional[str] = typer.Option(None, "--type", help="Filter models by type (dedicated: models that can be deployed as dedicated endpoints)"),
    json: bool = typer.Option(False, "--json", help="Output in JSON format")
) -> None:
    """List models"""
    client: Together = ctx.obj

    models_list = client.models.list(dedicated=type == "dedicated" if type else omit, timeout=1)

    if json:
        print(openapi_dumps(models_list))
        return


    table = rich_table.Table()
    table.add_column("Model")
    table.add_column("Type")
    table.add_column("Context length")
    table.add_column("Price per 1M Tokens (input/output)")

    # If the server has a bug and returns an empty .type this will crash if we don't do the or "".
    for model in sorted(models_list, key=lambda x: x.type or ""):  # type: ignore
        price_parts: List[str] = []

        # Only show pricing if a value actually exists
        if model.pricing and model.pricing.input > 0 and model.pricing.output > 0:
            price_parts.append(f"${model.pricing.input:.2f}")
            price_parts.append(f"${model.pricing.output:.2f}")

        table.add_row(model.id, model.type, str(model.context_length) if model.context_length else None, "/".join(price_parts))

    print(table)
