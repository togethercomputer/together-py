import typer

from .list import list
from .upload import upload

models = typer.Typer(help="Model discovery and management", short_help="Manage models", no_args_is_help=True, context_settings={"help_option_names": []})

models.command(short_help="List available models for inference, deployment, fine-tuning and more", context_settings={"help_option_names": ['--help', '-h']})(list)
models.command(short_help="Upload custom models", no_args_is_help=True)(upload)
