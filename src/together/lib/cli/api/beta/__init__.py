import typer

# from together.lib.cli.api.beta.jig import jig
# from together.lib.cli.api.beta.clusters import clusters

beta = typer.Typer(help="Beta API commands", no_args_is_help=True, context_settings={"help_option_names": []})


# @click.group()
# def beta() -> None:
#     """Beta API commands"""
#     pass


# beta.add_command(clusters)
# beta.add_command(jig)
