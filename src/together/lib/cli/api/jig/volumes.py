"""Volume management commands for jig."""

from __future__ import annotations

import asyncio
import json

import click
import httpx

from ._helpers import AppContext, create_volume, update_volume


@click.group()
@click.pass_context
def volumes(ctx: click.Context) -> None:
    """Manage volumes"""
    pass


@volumes.command("create")
@click.pass_context
@click.option("--name", required=True, help="Volume name")
@click.option("--source", required=True, help="Source directory path")
def volumes_create(ctx: click.Context, name: str, source: str) -> None:
    """Create a volume"""
    app_ctx: AppContext = ctx.obj
    asyncio.run(create_volume(app_ctx, name, source))


@volumes.command("update")
@click.pass_context
@click.option("--name", required=True, help="Volume name")
@click.option("--source", required=True, help="New source directory path")
def volumes_update(ctx: click.Context, name: str, source: str) -> None:
    """Update a volume"""
    app_ctx: AppContext = ctx.obj
    asyncio.run(update_volume(app_ctx, name, source))


@volumes.command("set")
@click.pass_context
@click.option("--name", required=True, help="Volume name")
@click.option("--mount-path", required=True, help="Mount path in container")
def volumes_set(ctx: click.Context, name: str, mount_path: str) -> None:
    """Set volume mount configuration for deployment"""
    app_ctx: AppContext = ctx.obj

    if len(app_ctx.state.volumes) > 0 and name not in app_ctx.state.volumes:
        raise click.ClickException("Only one read-only volume is supported per deployment")

    app_ctx.state.volumes[name] = mount_path
    app_ctx.state.save()
    click.echo(f"\N{CHECK MARK} Volume '{name}' will be mounted at '{mount_path}' during deployment")


@volumes.command("delete")
@click.pass_context
@click.option("--name", required=True, help="Volume name")
def volumes_delete(ctx: click.Context, name: str) -> None:
    """Delete a volume"""
    app_ctx: AppContext = ctx.obj

    try:
        app_ctx.client.request("DELETE", f"/v1/storage/volumes/{name}")
        click.echo(f"\N{CHECK MARK} Deleted volume '{name}'")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            click.echo(f"\N{CROSS MARK} Volume '{name}' not found")
            return
        raise

    if name in app_ctx.state.volumes:
        del app_ctx.state.volumes[name]
        app_ctx.state.save()
        click.echo(f"\N{CHECK MARK} Removed volume '{name}' from deployment configuration")


@volumes.command("describe")
@click.pass_context
@click.option("--name", required=True, help="Volume name")
def volumes_describe(ctx: click.Context, name: str) -> None:
    """Describe a volume"""
    app_ctx: AppContext = ctx.obj

    try:
        response = app_ctx.client.request("GET", f"/v1/storage/volumes/{name}")
        click.echo(json.dumps(response, indent=2))
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            click.echo(f"\N{CROSS MARK} Volume '{name}' not found")
            return
        raise


@volumes.command("list")
@click.pass_context
def volumes_list(ctx: click.Context) -> None:
    """List all volumes"""
    app_ctx: AppContext = ctx.obj

    response = app_ctx.client.request("GET", "/v1/storage/volumes")
    click.echo(json.dumps(response, indent=2))
