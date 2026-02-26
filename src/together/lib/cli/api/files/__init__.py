import typer

# from .list import list
# from .check import check
# from .delete import delete
# from .upload import upload
# from .retrieve import retrieve
# from .retrieve_content import retrieve_content


files = typer.Typer(help="Manage files", no_args_is_help=True, context_settings={"help_option_names": []})


# files.add_command(upload)
# files.add_command(list)
# files.add_command(retrieve)
# files.add_command(retrieve_content)
# files.add_command(delete)
# files.add_command(check)
