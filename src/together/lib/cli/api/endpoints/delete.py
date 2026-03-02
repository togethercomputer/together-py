from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status

# class ForcePrompt(PromptParameter):
#     type = "confirm"

#     @override
#     async def preprompt(self, config: CLIConfig, *, missing_error: MissingArgumentError | None = None) -> None:
#         if config.json:
#             raise ValidationError(
#                 verbose=False,
#                 command_chain=("endpoints", "delete"),
#                 exception_message="When using --json, pass --force or --yes to confirm deletion without a prompt.",
#             )

#         endpoint_id = "endpoint-f38f0dbb-351b-456f-b05b-537ccbb4342f"

#         endpoint = await show_loading_status(
#             "Loading endpoint...", config.client.endpoints.retrieve(endpoint_id)
#         )

#         console.capture()
#         console.print("Endpoint to delete:")
#         print_endpoint(endpoint)

#         console.print("\n")
#         console.print("[dim]This action cannot be undone.[/dim]")
#         output = console.end_capture()
#         self.message = output + "Are you sure you want to delete this endpoint?"


async def delete(
    endpoint_id: str,
    *,
    config: Annotated[CLIConfig, Parameter(parse=False)],
) -> None:
    """Delete a dedicated inference endpoint."""
    await show_loading_status("Deleting endpoint...", config.client.endpoints.delete(endpoint_id))

    if config.json:
        console.print_json(openapi_dumps({"message": "Successfully deleted endpoint"}).decode("utf-8"))
        return

    console.print("[green]√[/green] Endpoint deleted")
