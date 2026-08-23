from __future__ import annotations

import asyncio
from typing import Optional, Annotated

from cyclopts import Parameter

from together import APIError, omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils._exit import CliDiagnosticExit
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.endpoints._utils import print_endpoint, handle_endpoint_api_errors

from .hardware import hardware as list_hardware

ModelParameter = Annotated[str, Parameter(help="The model to deploy")]
MinReplicasParameter = Annotated[int, Parameter(help="Minimum number of replicas to deploy (must be >= 0)")]
MaxReplicasParameter = Annotated[int, Parameter(help="Maximum number of replicas to deploy (must be >= 0)")]
HardwareParameter = Annotated[Optional[str], Parameter(help="Hardware configuration to use for inference")]
DisplayNameParameter = Annotated[Optional[str], Parameter(help="A human-readable name for the endpoint")]
NoPromptCacheParameter = Annotated[
    Optional[bool], Parameter(help="Deprecated and no longer has any effect", negative=False, show=False)
]
NoSpeculativeDecodingParameter = Annotated[
    bool, Parameter(help="Disable speculative decoding for this endpoint", negative=False)
]
NoAutoStartParameter = Annotated[
    bool, Parameter(help="Create the endpoint in STOPPED state instead of auto-starting it", negative=False)
]
InactiveTimeoutParameter = Annotated[
    Optional[int],
    Parameter(help="Minutes of inactivity before the endpoint auto-stops (0 to disable)"),
]
AvailabilityZoneParameter = Annotated[
    Optional[str], Parameter(help="Start endpoint in specified availability zone (e.g. us-central-4b)")
]
WaitParameter = Annotated[bool, Parameter(help="Wait for the endpoint to be ready after creation", negative=False)]


@handle_endpoint_api_errors("Endpoints")
async def create(
    model: ModelParameter,
    min_replicas: MinReplicasParameter = 1,
    max_replicas: MaxReplicasParameter = 1,
    hardware: HardwareParameter = None,
    display_name: DisplayNameParameter = None,
    no_prompt_cache: NoPromptCacheParameter = None,
    no_speculative_decoding: NoSpeculativeDecodingParameter = False,
    no_auto_start: NoAutoStartParameter = False,
    inactive_timeout: InactiveTimeoutParameter = None,
    availability_zone: AvailabilityZoneParameter = None,
    wait: WaitParameter = False,
    *,
    config: CLIConfigParameter,
) -> None:
    """Create a new dedicated inference endpoint."""
    if min_replicas > max_replicas:
        console.print(
            f"Error: --min-replicas ({min_replicas}) cannot be greater than --max-replicas ({max_replicas})",
        )
        raise CliDiagnosticExit("Endpoint minimum replicas cannot exceed maximum replicas")

    if availability_zone:
        try:
            valid_zones = await config.client.endpoints.list_avzones()
            if availability_zone not in valid_zones.avzones:
                console.print(f"Error: Invalid availability zone '{availability_zone}'")
                if valid_zones.avzones:
                    console.print("Available zones:")
                    for zone in sorted(valid_zones.avzones):
                        console.print(f"  {zone}")
                raise CliDiagnosticExit("Endpoint availability zone is invalid")
        except Exception:
            pass

    if config.json and wait:
        console.print("Error: --json and --wait cannot be used together.")
        return

    if no_prompt_cache is not None and not config.json:
        console.print("Warning: --no-prompt-cache is deprecated and no longer has any effect.")

    try:
        response = await show_loading_status(
            "Creating endpoint...",
            config.client.endpoints.create(
                model=model,
                hardware=hardware or "",
                autoscaling={"min_replicas": min_replicas, "max_replicas": max_replicas},
                display_name=display_name or omit,
                disable_speculative_decoding=no_speculative_decoding or omit,
                state="STOPPED" if no_auto_start else "STARTED",
                inactive_timeout=inactive_timeout,
                extra_query={"availability_zone": availability_zone or omit},
            ),
        )
    except APIError as e:
        if config.json:
            raise e
        error_msg = str(e.args[0]).lower() if e.args else ""
        if (
            "check the hardware api" in error_msg
            or "invalid hardware provided" in error_msg
            or "invalid hardware/gpu provided" in error_msg
            or "the selected configuration" in error_msg
            or "hardware is required" in error_msg
        ):
            console.print("Invalid hardware selected." if hardware else "Missing required argument --hardware")
            await list_hardware(model=model, config=config, available=True)
            diagnostic = "Endpoint hardware is invalid" if hardware else "Endpoint hardware is required"
            raise CliDiagnosticExit(diagnostic) from None
        elif "model" in error_msg and (
            "not found" in error_msg
            or "invalid" in error_msg
            or "does not exist" in error_msg
            or "not supported" in error_msg
        ):
            console.print(f"Error: Model '{model}' was not found or is not available for dedicated endpoints.")
            console.print(
                "Please check that the model name is correct and that it supports dedicated endpoint deployment.",
            )
            console.print("You can browse available models at: https://api.together.ai/models")
            raise CliDiagnosticExit("Endpoint model is unavailable") from None
        raise e

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print("[green]√[/green] Dedicated endpoint created.")
    print_endpoint(response)

    if wait:
        with console.status(
            "[progress.description]Waiting for endpoint to start...[/progress.description]",
            spinner="dots",
            spinner_style="bar.pulse",
        ):
            while (await config.client.endpoints.retrieve(response.id)).state != "STARTED":
                await asyncio.sleep(1)
        console.print("[green]√[/green] Endpoint started")
