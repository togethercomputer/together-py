import click

from .list import list
from .upload import upload


@click.group()
@click.pass_context
def models(ctx: click.Context) -> None:
    """Models API commands"""
    pass


models.add_command(list)
models.add_command(upload)
