import typer

from .list import list
# from .cancel import cancel
from .create import create
# from .delete import delete
# from .download import download
# from .retrieve import retrieve
# from .list_events import list_events
# from .list_checkpoints import list_checkpoints


fine_tuning = typer.Typer(help="Run and manage FineTuning workflows", no_args_is_help=True)

fine_tuning.command()(create)
fine_tuning.command(help="List Fine Tuning jobs and their status")(list)
# fine_tuning.add_command(retrieve)
# fine_tuning.add_command(cancel)
# fine_tuning.add_command(list_events)
# fine_tuning.add_command(list_checkpoints)
# fine_tuning.add_command(download)
# fine_tuning.add_command(delete)
