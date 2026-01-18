import click

from .list import list
from .create import create
from .status import status
from .retrieve import retrieve


@click.group()
@click.pass_context
def evals(ctx: click.Context) -> None:
    """Evals API commands"""
    pass


evals.add_command(create)
evals.add_command(list)
evals.add_command(retrieve)
evals.add_command(status)
