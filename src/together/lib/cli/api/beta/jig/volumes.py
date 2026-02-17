"""Volume management CLI commands for jig."""

from __future__ import annotations

import json
import asyncio
from pathlib import Path

import click

from together import Together
from together._exceptions import APIStatusError
from together.lib.cli.api._utils import handle_api_errors
from together.lib.cli.api.beta.jig._uploader import Uploader


@click.group()
@click.pass_context
def volumes(ctx: click.Context) -> None:
    """Manage volumes"""
    pass


# --- File upload ---


async def _create_volume(client: Together, name: str, source: str) -> None:
    """Create a volume and upload files"""
    source_path = Path(source)
    if not source_path.exists():
        raise ValueError(f"Source path does not exist: {source}")
    if not source_path.is_dir():
        raise ValueError(f"Source path must be a directory: {source}")

    source_prefix = f"{name}/{source_path.name}"

    click.echo(f"\N{ROCKET} Creating volume '{name}' with source prefix '{source_prefix}'")
    try:
        volume_response = client.beta.jig.volumes.create(
            name=name,
            type="readOnly",
            content={"type": "files", "source_prefix": source_prefix},
        )
        click.echo(f"\N{CHECK MARK} Volume created: {volume_response.id}")
    except Exception as e:
        raise RuntimeError(f"Failed to create volume: {e}") from e

    try:
        await Uploader(client).upload_files(source_path, volume_name=name)
    except Exception as e:
        click.echo(f"\N{CROSS MARK} Upload failed: {e}")
        click.echo(f"\N{WASTEBASKET} Cleaning up volume '{name}'")
        try:
            client.beta.jig.volumes.delete(name)
        except Exception as cleanup_error:
            click.echo(f"\N{WARNING SIGN} Failed to delete volume: {cleanup_error}")
        raise


async def _update_volume(client: Together, name: str, source: str) -> None:
    """Update a volume and re-upload files"""
    source_path = Path(source)
    if not source_path.exists():
        raise ValueError(f"Source path does not exist: {source}")
    if not source_path.is_dir():
        raise ValueError(f"Source path must be a directory: {source}")

    try:
        client.beta.jig.volumes.retrieve(name)
    except APIStatusError as e:
        if hasattr(e, "status_code") and e.status_code == 404:
            raise ValueError(f"Volume '{name}' does not exist") from e
        raise

    source_prefix = f"{name}/{source_path.name}"

    click.echo(f"\N{INFORMATION SOURCE} Uploading files for volume '{name}'")
    await Uploader(client).upload_files(source_path, volume_name=name)

    click.echo(f"\N{INFORMATION SOURCE} Updating volume '{name}' with source prefix '{source_prefix}'")
    client.beta.jig.volumes.update(
        name,
        content={"type": "files", "source_prefix": source_prefix},
    )
    click.echo("\N{CHECK MARK} Volume updated successfully")


# --- CLI Commands ---


@volumes.command("create")
@click.pass_context
@click.option("--name", required=True, help="Volume name")
@click.option("--source", required=True, help="Source directory path")
@handle_api_errors("Volumes")
def volumes_create(
    ctx: click.Context,
    name: str,
    source: str,
) -> None:
    """Create a volume and upload files"""
    client: Together = ctx.obj
    asyncio.run(_create_volume(client, name, source))


@volumes.command("update")
@click.pass_context
@click.option("--name", required=True, help="Volume name")
@click.option("--source", required=True, help="New source directory path")
@handle_api_errors("Volumes")
def volumes_update(
    ctx: click.Context,
    name: str,
    source: str,
) -> None:
    """Update a volume and re-upload files"""
    client: Together = ctx.obj
    asyncio.run(_update_volume(client, name, source))


@volumes.command("delete")
@click.pass_context
@click.option("--name", required=True, help="Volume name")
@handle_api_errors("Volumes")
def volumes_delete(
    ctx: click.Context,
    name: str,
) -> None:
    """Delete a volume"""
    client: Together = ctx.obj

    try:
        client.beta.jig.volumes.delete(name)
        click.echo(f"\N{CHECK MARK} Deleted volume '{name}'")
    except APIStatusError as e:
        if hasattr(e, "status_code") and e.status_code == 404:
            click.echo(f"\N{CROSS MARK} Volume '{name}' not found")
            return
        raise


@volumes.command("describe")
@click.pass_context
@click.option("--name", required=True, help="Volume name")
@handle_api_errors("Volumes")
def volumes_describe(
    ctx: click.Context,
    name: str,
) -> None:
    """Describe a volume"""
    client: Together = ctx.obj

    try:
        response = client.beta.jig.volumes.with_raw_response.retrieve(name)
        click.echo(json.dumps(response.json(), indent=2))
    except APIStatusError as e:
        if hasattr(e, "status_code") and e.status_code == 404:
            click.echo(f"\N{CROSS MARK} Volume '{name}' not found")
            return
        raise


@volumes.command("list")
@click.pass_context
@handle_api_errors("Volumes")
def volumes_list(ctx: click.Context) -> None:
    """List all volumes"""
    client: Together = ctx.obj
    response = client.beta.jig.volumes.with_raw_response.list()
    click.echo(json.dumps(response.json(), indent=2))
