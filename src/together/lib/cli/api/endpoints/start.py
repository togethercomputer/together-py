from __future__ import annotations

import json as json_lib
import sys
from typing import Annotated
from typing_extensions import override

from cyclopts import Parameter

import asyncio
import questionary

from together.lib.cli.logger.config import CLIConfig
from together.lib.cli.logger.prompt import PromptParameter, console
from together.lib.utils.serializer import datetime_serializer

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
                if endpoint.id is None: # type: ignore
                    continue

                if endpoint.state != "STARTED":
                    self.choices.append(questionary.Choice(title=[("", endpoint.name), ("class:disabled", " ({})".format(endpoint.id))], value=endpoint.id))


async def start(
    endpoint_id: Annotated[str, Parameter(required=True, help="The ID of the endpoint to start"), LoadEndpointsPrompt(message="Enter the endpoint ID")],
    wait: bool = False,
    *,
    config: Annotated[CLIConfig, Parameter(parse=False)],
) -> None:
    """Start a dedicated inference endpoint."""
    response = await config.client.endpoints.update(endpoint_id, state="STARTED")
    

    if config.json:
        print(json_lib.dumps(response.model_dump(), default=datetime_serializer, indent=2))
        return

    print("Successfully marked endpoint as starting", file=sys.stderr)
    if wait:
        print("Waiting for endpoint to start...", file=sys.stderr)
        while (await config.client.endpoints.retrieve(endpoint_id)).state != "STARTED":
            await asyncio.sleep(1)
        print("Endpoint started", file=sys.stderr)
    print(endpoint_id)
