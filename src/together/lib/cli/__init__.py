from __future__ import annotations

import os
import sys
from typing import Any

import click
import httpx

import together
from together._version import __version__
from together._constants import DEFAULT_TIMEOUT
from together._utils._logs import setup_logging
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
    if debug:
        os.environ.setdefault("TOGETHER_LOG", "debug")
        setup_logging()  # Must run this again here to allow the new logging configuration to take effect

    try:
        ctx.obj = together.Together(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries if max_retries is not None else 0,
        )

    # This implementation is indeed strange, but it's the best user experience for the CLI when the api key is not set
    # The constructor will raise an error if there is no api key set. We catch the error and you may think a simpler implementation
    # would be just to print the error right away and exit. Unfortunately that means that the user would not be able to see any usage commands.
    # E.g. if they type `together models` it would print the error and exit without showing any usage commands.
    #
    # Instead we opt to create a dummy client and hook into any requests performed by the client. We take that moment to print the error and exit.
    except Exception as e:
        if "api_key" in str(e):
            ctx.obj = together.Together(
                api_key="0000000000000000000000000000000000000000",
                base_url=base_url,
                timeout=timeout,
                max_retries=max_retries if max_retries is not None else 0,
            )

            # Wrap the client's httpx requests to track the parameters sent on api requests
            def block_requests_for_api_key(_: httpx.Request) -> None:
                invoked_command = click.get_current_context().command_path
                invoked_command_name = invoked_command.split("together ")[1]
                click.secho(
                    "Error: api key missing.\n\nThe api_key must be set either by passing --api-key to the command or by setting the TOGETHER_API_KEY environment variable",
                    fg="red",
                )
                click.secho("\nYou can find your api key at https://api.together.xyz/settings/api-keys", fg="yellow")
                click.secho(f"\nUsage: together --api-key <your-api-key> {invoked_command_name}", fg="yellow")
                sys.exit(1)

            ctx.obj._client.event_hooks["request"].append(block_requests_for_api_key)
            return

        raise e


main.add_command(files)
main.add_command(fine_tuning)
main.add_command(models)
main.add_command(endpoints)
main.add_command(evals)
main.add_command(beta)

if __name__ == "__main__":
    main()
