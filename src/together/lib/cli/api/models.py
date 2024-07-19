from typing import Any, List
from textwrap import wrap

import click
from tabulate import tabulate

from together import Together


@click.group()
@click.pass_context
def models(_ctx: click.Context) -> None:
    """Models API commands"""
    pass


@models.command()
@click.pass_context
def list(ctx: click.Context) -> None:
    """List models"""
    client: Together = ctx.obj

    response = client.models.list()

    display_list: List[dict[str, Any]] = []

    for model in response:
        display_list.append(
            {
                "ID": "\n".join(wrap(model.id or "", width=30)),
                "Name": "\n".join(wrap(model.display_name or "", width=30)),
                "Organization": model.organization,
                "Type": model.type,
                "Context Length": model.context_length,
                "License": "\n".join(wrap(model.license or "", width=30)),
                "Input per 1M token": model.pricing.input if model.pricing else None,
                "Output per 1M token": model.pricing.output if model.pricing else None,
            }
        )

    click.echo(tabulate(display_list, headers="keys", tablefmt="grid"))
