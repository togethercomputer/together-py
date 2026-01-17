import click

from .list import list
from .check import check
from .delete import delete
from .upload import upload
from .retrieve import retrieve
from .retrieve_content import retrieve_content


@click.group()
@click.pass_context
def files(ctx: click.Context) -> None:
    """File API commands"""
    pass


files.add_command(upload)
files.add_command(list)
files.add_command(retrieve)
files.add_command(retrieve_content)
files.add_command(delete)
files.add_command(check)
