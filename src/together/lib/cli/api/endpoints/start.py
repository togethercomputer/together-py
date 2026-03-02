from __future__ import annotations

import asyncio
from typing import Annotated
from typing_extensions import override

import questionary
from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.utils._prompt import PromptParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status


class LoadEndpointsPrompt(PromptParameter):
    @override
    async def preprompt(self, config: CLIConfig):
        with console.status(
            "[progress.description]Loading endpoints...[/progress.description]",
            spinner="dots",
            spinner_style="bar.pulse",
        ):
            endpoints = await config.client.endpoints.list()
            self.choices = []
            for endpoint in endpoints.data:
                # This shouldn't happen.. but does happen sometimes...
                if endpoint.id is None:  # type: ignore
                    continue

                if endpoint.state != "STARTED":
                    self.choices.append(
                        questionary.Choice(
                            title=[("", endpoint.name), ("class:disabled", " ({})".format(endpoint.id))],
                            value=endpoint.id,
                        )
                    )


async def start(
    endpoint_id: Annotated[
        str,
        Parameter(required=True, help="The ID of the endpoint to start"),
        LoadEndpointsPrompt(message="Enter the endpoint ID"),
    ],
    wait: bool = False,
    *,
    config: Annotated[CLIConfig, Parameter(parse=False)],
) -> None:
    """Start a dedicated inference endpoint."""
    response = await show_loading_status(
        "Starting endpoint...", config.client.endpoints.update(endpoint_id, state="STARTED")
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    if wait:
        console.print("[green]√[/green] Successfully requested endpoint to start.")
        with console.status(
            "[progress.description]Waiting for endpoint to start...[/progress.description]",
            spinner="dots",
            spinner_style="bar.pulse",
        ):
            while (await config.client.endpoints.retrieve(endpoint_id)).state != "STARTED":
                await asyncio.sleep(1)
        console.print("[green]√[/green] Endpoint started")
    else:
        console.print("[green]√[/green] Endpoint is starting.\n  This may take a few minutes.")
