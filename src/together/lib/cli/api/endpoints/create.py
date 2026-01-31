from __future__ import annotations

import sys

import click

from together import APIError, Together, omit
from together.lib.cli.api._utils import handle_api_errors

from .hardware import hardware


@click.command()
@click.option(
    "--model",
    required=True,
    help="The model to deploy (e.g. meta-llama/Llama-4-Scout-17B-16E-Instruct)",
)
@click.option(
    "--min-replicas",
    type=int,
    default=1,
    help="Minimum number of replicas to deploy",
)
@click.option(
    "--max-replicas",
    type=int,
    default=1,
    help="Maximum number of replicas to deploy",
)
@click.option(
    "--gpu",
    type=click.Choice(["b200", "h200", "h100", "a100", "l40", "l40s", "rtx-6000"]),
    required=True,
    help="GPU type to use for inference",
)
@click.option(
    "--gpu-count",
    type=int,
    default=1,
    help="Number of GPUs to use per replica",
)
@click.option(
    "--display-name",
    help="A human-readable name for the endpoint",
)
@click.option(
    "--no-prompt-cache",
    is_flag=True,
    help="Deprecated and no longer has any effect.",
)
@click.option(
    "--no-speculative-decoding",
    is_flag=True,
    help="Disable speculative decoding for this endpoint",
)
@click.option(
    "--no-auto-start",
    is_flag=True,
    help="Create the endpoint in STOPPED state instead of auto-starting it",
)
@click.option(
    "--inactive-timeout",
    type=int,
    help="Number of minutes of inactivity after which the endpoint will be automatically stopped. Set to 0 to disable.",
)
@click.option(
    "--availability-zone",
    help="Start endpoint in specified availability zone (e.g., us-central-4b)",
)
@click.option(
    "--wait/--no-wait",
    default=True,
    help="Wait for the endpoint to be ready after creation",
)
@click.pass_context
@handle_api_errors("Endpoints")
def create(
    ctx: click.Context,
    model: str,
    min_replicas: int,
    max_replicas: int,
    gpu: str,
    gpu_count: int,
    display_name: str | None,
    no_prompt_cache: bool | None,
    no_speculative_decoding: bool | None,
    no_auto_start: bool,
    inactive_timeout: int | None,
    availability_zone: str | None,
    wait: bool,
) -> None:
    """Create a new dedicated inference endpoint."""
    client: Together = ctx.obj
    # Map GPU types to their full hardware ID names
    gpu_map = {
        "b200": "nvidia_b200_180gb_sxm",
        "h200": "nvidia_h200_140gb_sxm",
        "h100": "nvidia_h100_80gb_sxm",
        "a100": "nvidia_a100_80gb_pcie" if gpu_count == 1 else "nvidia_a100_80gb_sxm",
        "l40": "nvidia_l40",
        "l40s": "nvidia_l40s",
        "rtx-6000": "nvidia_rtx_6000_ada",
    }

    if no_prompt_cache is not None:
        click.echo("Warning: --no-prompt-cache is deprecated and no longer has any effect.", err=True)

    hardware_id = f"{gpu_count}x_{gpu_map[gpu]}"

    try:
        response = client.endpoints.create(
            model=model,
            hardware=hardware_id,
            autoscaling={
                "min_replicas": min_replicas,
                "max_replicas": max_replicas,
            },
            display_name=display_name or omit,
            disable_speculative_decoding=no_speculative_decoding or omit,
            state="STOPPED" if no_auto_start else "STARTED",
            inactive_timeout=inactive_timeout,
            extra_query={"availability_zone": availability_zone or omit},
        )
    except APIError as e:
        if (
            "check the hardware api" in str(e.args[0]).lower()
            or "invalid hardware provided" in str(e.args[0]).lower()
            or "the selected configuration" in str(e.args[0]).lower()
        ):
            click.secho("Invalid hardware selected.", fg="red", err=True)
            click.echo("\nAvailable hardware options:")
            ctx.invoke(hardware, available=True, model=model, json=False)
            sys.exit(1)
        raise e

    # Print detailed information to stderr
    click.echo("Created dedicated endpoint with:", err=True)
    click.echo(f"  Model: {model}", err=True)
    click.echo(f"  Min replicas: {min_replicas}", err=True)
    click.echo(f"  Max replicas: {max_replicas}", err=True)
    click.echo(f"  Hardware: {hardware_id}", err=True)
    if display_name:
        click.echo(f"  Display name: {display_name}", err=True)
    if no_speculative_decoding:
        click.echo("  Speculative decoding: disabled", err=True)
    if no_auto_start:
        click.echo("  Auto-start: disabled", err=True)
    if inactive_timeout is not None:
        click.echo(f"  Inactive timeout: {inactive_timeout} minutes", err=True)
    if availability_zone:
        click.echo(f"  Availability zone: {availability_zone}", err=True)

    click.echo(f"Endpoint created successfully, id: {response.id}", err=True)

    if wait:
        import time

        click.echo("Waiting for endpoint to be ready...", err=True)
        while client.endpoints.retrieve(response.id).state != "STARTED":
            time.sleep(1)
        click.echo("Endpoint ready", err=True)

    # Print only the endpoint ID to stdout
    click.echo(response.id)
