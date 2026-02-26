import typer

# from .list import list
# from .create import create
# from .status import status
# from .retrieve import retrieve

evals = typer.Typer(help="Run and manage Evals workflows", no_args_is_help=True, context_settings={"help_option_names": []})

# evals.add_command(create)
# evals.add_command(list)
# evals.add_command(retrieve)
# evals.add_command(status)
