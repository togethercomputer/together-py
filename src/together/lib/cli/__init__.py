from __future__ import annotations

import os
import sys
from typing import Optional

from rich import print
import httpx
import typer

import together
from together._constants import DEFAULT_TIMEOUT
from together._utils._logs import setup_logging
from together._version import __version__
from together.lib.cli.api.beta import beta
from together.lib.cli.api.evals import evals
from together.lib.cli.api.files import files
from together.lib.cli.api.models import models
from together.lib.cli.api.endpoints import endpoints
from together.lib.cli.api.fine_tuning import fine_tuning

app = typer.Typer(
    name="together",
    help=f"TogetherAI CLI {__version__}",
    no_args_is_help=True,
    context_settings={"help_option_names": []},
)

@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        envvar="TOGETHER_API_KEY",
        hidden=True,
        help="API Key. Defaults to environment variable `TOGETHER_API_KEY`",
    ),
    base_url: Optional[str] = typer.Option(None, "--base-url", hidden=True, help="API Base URL. Defaults to Together AI endpoint."),
    timeout: Optional[int] = typer.Option(None, "--timeout", hidden=True, help=f"Request timeout. Defaults to {DEFAULT_TIMEOUT} seconds"),
    max_retries: Optional[int] = typer.Option(None, "--max-retries", hidden=True, help="Maximum number of HTTP retries."),
    version_flag: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Print version",
    ),
    debug: Optional[bool] = typer.Option(False, "--debug", "-d", hidden=True, help="Debug mode"),
) -> None:
    """Together AI CLI"""
    if version_flag:
        typer.echo(f"TogetherAI CLI version: {__version__}")
        raise typer.Exit()

    if debug:
        os.environ.setdefault("TOGETHER_LOG", "debug")
        setup_logging()

    try:
        ctx.obj = together.Together(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries if max_retries is not None else 0,
        )
    except Exception as e:
        if "api_key" in str(e):
            ctx.obj = together.Together(
                api_key="0000000000000000000000000000000000000000",
                base_url=base_url,
                timeout=timeout,
                max_retries=max_retries if max_retries is not None else 0,
            )

            def block_requests_for_api_key(_: httpx.Request) -> None:
                invoked_command = ctx.invoked_subcommand or ""
                invoked_command_name = invoked_command.split("together ")[1]
                typer.secho(
                    "Error: api key missing.\n\nThe api_key must be set either by passing --api-key to the command or by setting the TOGETHER_API_KEY environment variable",
                    fg="red",
                )
                typer.secho("\nYou can find your api key at https://api.together.xyz/settings/api-keys", fg="yellow")
                typer.secho(f"\nUsage: together --api-key <your-api-key> {invoked_command_name}", fg="yellow")
                sys.exit(1)

            ctx.obj._client.event_hooks["request"].append(block_requests_for_api_key)
            return
        raise e

# Create the main app with the callback that sets up ctx.obj
app.add_typer(files, name="files")
app.add_typer(fine_tuning, name="fine-tuning")
app.add_typer(models, name="models")
app.add_typer(endpoints, name="endpoints")
app.add_typer(evals, name="evals")
app.add_typer(beta, name="beta")

def main() -> None:
    """Entry point for the CLI"""
    try:
        app()
    except typer.Abort:
        typer.echo("\nOperation cancelled")
        raise typer.Exit(0)
    except together.APIError as e:
        error_msg = ""
        if e.body is not None:
            error_msg = getattr(e.body, "message", str(e.body))
        else:
            error_msg = str(e)
        print(f"[bold red]{e.__class__.__name__}:[/bold red] {error_msg}")
        sys.exit(1)
    except Exception as e:
        print(f"[bold red]{e.__class__.__name__}:[/bold red] An unexpected error occurred - {str(e)}")
        sys.exit(1)
