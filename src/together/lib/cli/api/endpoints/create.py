from __future__ import annotations

import asyncio
import sys
from typing import Annotated, Optional

from cyclopts import Parameter

from together import APIError, AsyncTogether, omit

from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors

from .hardware import hardware as list_hardware


@handle_endpoint_api_errors("Endpoints")
async def create(
    model: str,
    min_replicas: int = 1,
    max_replicas: int = 1,
    hardware: Optional[str] = None,
    display_name: Optional[str] = None,
    no_prompt_cache: Optional[bool] = None,
    no_speculative_decoding: bool = False,
    no_auto_start: bool = False,
    inactive_timeout: Optional[int] = None,
    availability_zone: Optional[str] = None,
    wait: bool = False,
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Create a new dedicated inference endpoint."""
    if min_replicas > max_replicas:
        print(
            f"Error: --min-replicas ({min_replicas}) cannot be greater than --max-replicas ({max_replicas})",
            file=sys.stderr,
        )
        sys.exit(1)

    if availability_zone:
        try:
            valid_zones = await client.endpoints.list_avzones()
            if availability_zone not in valid_zones.avzones:
                print(f"Error: Invalid availability zone '{availability_zone}'", file=sys.stderr)
                if valid_zones.avzones:
                    print("Available zones:", file=sys.stderr)
                    for zone in sorted(valid_zones.avzones):
                        print(f"  {zone}", file=sys.stderr)
                sys.exit(1)
        except Exception:
            pass

    if json_output and wait:
        print("Error: --json and --wait cannot be used together.", file=sys.stderr)
        return

    if no_prompt_cache is not None and not json_output:
        print("Warning: --no-prompt-cache is deprecated and no longer has any effect.", file=sys.stderr)

    if hardware is None:
        print("Error: --hardware is required", file=sys.stderr)
        sys.exit(1)

    try:
        response = await client.endpoints.create(
            model=model,
            hardware=hardware,
            autoscaling={"min_replicas": min_replicas, "max_replicas": max_replicas},
            display_name=display_name or omit,
            disable_speculative_decoding=no_speculative_decoding or omit,
            state="STOPPED" if no_auto_start else "STARTED",
            inactive_timeout=inactive_timeout,
            extra_query={"availability_zone": availability_zone or omit},
        )
    except APIError as e:
        if json_output:
            raise e
        error_msg = str(e.args[0]).lower() if e.args else ""
        if (
            "check the hardware api" in error_msg
            or "invalid hardware provided" in error_msg
            or "the selected configuration" in error_msg
            or "hardware is required" in error_msg
        ):
            print("Invalid hardware selected.", file=sys.stderr)
            print("\nAvailable hardware options:", file=sys.stderr)
            await list_hardware(model=model, json_output=False, available=True, client=client)
            sys.exit(1)
        elif "model" in error_msg and (
            "not found" in error_msg
            or "invalid" in error_msg
            or "does not exist" in error_msg
            or "not supported" in error_msg
        ):
            print(f"Error: Model '{model}' was not found or is not available for dedicated endpoints.", file=sys.stderr)
            print("Please check that the model name is correct and that it supports dedicated endpoint deployment.", file=sys.stderr)
            print("You can browse available models at: https://api.together.ai/models", file=sys.stderr)
            sys.exit(1)
        raise e

    if json_output:
        print(response.model_dump_json(indent=2))
        return

    print("Created dedicated endpoint with:", file=sys.stderr)
    print(f"  Model: {model}", file=sys.stderr)
    print(f"  Min replicas: {min_replicas}", file=sys.stderr)
    print(f"  Max replicas: {max_replicas}", file=sys.stderr)
    print(f"  Hardware: {hardware}", file=sys.stderr)
    if display_name:
        print(f"  Display name: {display_name}", file=sys.stderr)
    if no_speculative_decoding:
        print("  Speculative decoding: disabled", file=sys.stderr)
    if no_auto_start:
        print("  Auto-start: disabled", file=sys.stderr)
    if inactive_timeout is not None:
        print(f"  Inactive timeout: {inactive_timeout} minutes", file=sys.stderr)
    if availability_zone:
        print(f"  Availability zone: {availability_zone}", file=sys.stderr)
    print(f"Endpoint created successfully, id: {response.id}", file=sys.stderr)

    if wait:
        print("Waiting for endpoint to be ready...", file=sys.stderr)
        while (await client.endpoints.retrieve(response.id)).state != "STARTED":
            await asyncio.sleep(1)
        print("Endpoint ready", file=sys.stderr)
    print(response.id)
