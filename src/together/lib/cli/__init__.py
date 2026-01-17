from __future__ import annotations

import os
from typing import Any

import click

import together
from together._version import __version__
from together._constants import DEFAULT_TIMEOUT
from together.lib.cli.api.beta import beta
from together.lib.cli.api.evals import evals
from together.lib.cli.api.files import files
from together.lib.cli.api.models import models
from together.lib.cli.api.endpoints import endpoints
from together.lib.cli.api.fine_tuning import fine_tuning


def print_version(ctx: click.Context, _params: Any, value: Any) -> None:
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"Version {__version__}")
    ctx.exit()


@click.group()
@click.pass_context
@click.option(
    "--api-key",
    type=str,
    help="API Key. Defaults to environment variable `TOGETHER_API_KEY`",
    default=os.getenv("TOGETHER_API_KEY"),
)
@click.option("--base-url", type=str, help="API Base URL. Defaults to Together AI endpoint.")
@click.option("--timeout", type=int, help=f"Request timeout. Defaults to {DEFAULT_TIMEOUT} seconds")
@click.option(
    "--max-retries",
    type=int,
    help=f"Maximum number of HTTP retries.",
)
@click.option(
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Print version",
)
@click.option("--debug", help="Debug mode", is_flag=True)
def main(
    ctx: click.Context,
    api_key: str | None,
    base_url: str | None,
    timeout: int | None,
    debug: bool | None,
    max_retries: int | None,
) -> None:
    """This is a sample CLI tool."""
    os.environ.setdefault("TOGETHER_LOG", "debug" if debug else "info")
    ctx.obj = together.Together(
        api_key=api_key, base_url=base_url, timeout=timeout, max_retries=max_retries if max_retries is not None else 0
    )


main.add_command(files)
main.add_command(fine_tuning)
main.add_command(models)
main.add_command(endpoints)
main.add_command(evals)
main.add_command(beta)

if __name__ == "__main__":
    main()
