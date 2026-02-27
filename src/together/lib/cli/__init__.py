from __future__ import annotations

import os
import sys
from typing_extensions import override

from rich import print
from clypi import Command, AbortException, arg

import together
from together._version import __version__
from together._utils._logs import setup_logging
from together.lib.cli.api.beta import Beta
from together.lib.cli.api.evals import Evals
from together.lib.cli.api.files import Files
from together.lib.cli.api.models import Models
from together.lib.cli.api.endpoints import Endpoints
from together.lib.cli.api.fine_tuning import FineTuning

from .api.models import Models


class Together(Command):
    subcommand: Models | FineTuning | Files | Evals | Endpoints | Beta | None

    api_key: str | None = arg(env="TOGETHER_API_KEY", hidden=True)
    base_url: str | None = arg(default=None, hidden=True)
    timeout: int | None = arg(default=None, hidden=True)
    debug: bool = arg(False, hidden=True)
    version: bool = arg(False, help="Print version", group="global")
    max_retries: int | None = arg(default=None, hidden=True)

    @override
    async def pre_run_hook(self) -> None:
        if self.version:
            print(f"Version {__version__}")
            exit(0)

        if self.debug:
            os.environ.setdefault("TOGETHER_LOG", "debug")
            setup_logging()  # Must run this again here to allow the new logging configuration to take effect

    @override
    async def run(self):
        self.print_help()


#     try:
#         ctx.obj = together.Together(
#             api_key=api_key,
#             base_url=base_url,
#             timeout=timeout,
#             max_retries=max_retries if max_retries is not None else 0,
#         )

#     # This implementation is indeed strange, but it's the best user experience for the CLI when the api key is not set
#     # The constructor will raise an error if there is no api key set. We catch the error and you may think a simpler implementation
#     # would be just to print the error right away and exit. Unfortunately that means that the user would not be able to see any usage commands.
#     # E.g. if they type `together models` it would print the error and exit without showing any usage commands.
#     #
#     # Instead we opt to create a dummy client and hook into any requests performed by the client. We take that moment to print the error and exit.
#     except Exception as e:
#         if "api_key" in str(e):
#             ctx.obj = together.Together(
#                 api_key="0000000000000000000000000000000000000000",
#                 base_url=base_url,
#                 timeout=timeout,
#                 max_retries=max_retries if max_retries is not None else 0,
#             )

#             # Wrap the client's httpx requests to track the parameters sent on api requests
#             def block_requests_for_api_key(_: httpx.Request) -> None:
#                 invoked_command = click.get_current_context().command_path
#                 invoked_command_name = invoked_command.split("together ")[1]
#                 click.secho(
#                     "Error: api key missing.\n\nThe api_key must be set either by passing --api-key to the command or by setting the TOGETHER_API_KEY environment variable",
#                     fg="red",
#                 )
#                 click.secho("\nYou can find your api key at https://api.together.xyz/settings/api-keys", fg="yellow")
#                 click.secho(f"\nUsage: together --api-key <your-api-key> {invoked_command_name}", fg="yellow")
#                 sys.exit(1)

#             ctx.obj._client.event_hooks["request"].append(block_requests_for_api_key)
#             return

#         raise e


def main():
    try:
        cli = Together.parse()
        cli.start()
    except AbortException as e:
        print("\nOperation cancelled")
        raise sys.exit(1) from e
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
