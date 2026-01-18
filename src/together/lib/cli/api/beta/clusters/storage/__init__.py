import click

from .list import list
from .create import create
from .delete import delete
from .retrieve import retrieve


@click.group()
@click.pass_context
def storage(ctx: click.Context) -> None:
    """Clusters Storage API commands"""
    pass


storage.add_command(create)
storage.add_command(retrieve)
storage.add_command(delete)
storage.add_command(list)
