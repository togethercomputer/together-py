import click

from .list import list
from .cancel import cancel
from .create import create
from .delete import delete
from .download import download
from .retrieve import retrieve
from .list_events import list_events
from .list_checkpoints import list_checkpoints


@click.group(name="fine-tuning")
@click.pass_context
def fine_tuning(ctx: click.Context) -> None:
    """Fine-tunes API commands"""
    pass


fine_tuning.add_command(create)
fine_tuning.add_command(list)
fine_tuning.add_command(retrieve)
fine_tuning.add_command(cancel)
fine_tuning.add_command(list_events)
fine_tuning.add_command(list_checkpoints)
fine_tuning.add_command(download)
fine_tuning.add_command(delete)
