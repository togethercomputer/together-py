"""Secrets management commands for jig."""

from __future__ import annotations

import click
import httpx

from ._helpers import AppContext


@click.group()
@click.pass_context
def secrets(ctx: click.Context) -> None:
    """Manage deployment secrets"""
    pass


@secrets.command("set")
@click.pass_context
@click.option("--name", required=True, help="Secret name")
@click.option("--value", required=True, help="Secret value")
@click.option("--description", default="", help="Secret description")
def secrets_set(ctx: click.Context, name: str, value: str, description: str) -> None:
    """Set a secret"""
    app_ctx: AppContext = ctx.obj

    deployment_secret_name = f"{app_ctx.config.model_name}-{name}"
    secret_data = {
        "name": deployment_secret_name,
        "description": description,
        "value": value,
    }

    try:
        app_ctx.client.request("GET", f"/v1/secrets/{deployment_secret_name}")
        app_ctx.client.request("PATCH", f"/v1/secrets/{deployment_secret_name}", json=secret_data)
        click.echo(f"\N{CHECK MARK} Updated secret: '{name}'")
    except httpx.HTTPStatusError as e:
        if e.response.status_code != 404:
            raise
        click.echo("\N{ROCKET} Creating new secret")
        app_ctx.client.request("POST", "/v1/secrets", json=secret_data)
        click.echo(f"\N{CHECK MARK} Created secret: {name}")

    app_ctx.state.secrets[name] = deployment_secret_name
    app_ctx.state.save()


@secrets.command("unset")
@click.pass_context
@click.option("--name", required=True, help="Secret name to remove")
def secrets_unset(ctx: click.Context, name: str) -> None:
    """Remove a secret"""
    app_ctx: AppContext = ctx.obj

    # FIXME: also delete secret from remote
    if app_ctx.state.secrets.pop(name, ""):
        app_ctx.state.save()
        click.echo("\N{CHECK MARK} Removed secret from deployment")
    else:
        click.echo(f"Secret {name} is not set")


@secrets.command("list")
@click.pass_context
def secrets_list(ctx: click.Context) -> None:
    """List all secrets"""
    app_ctx: AppContext = ctx.obj

    click.echo(f"\N{INFORMATION SOURCE} Following secrets are mapped to deployment {app_ctx.config.model_name}")
    for secret_name in app_ctx.state.secrets:
        click.echo(f"  - Secret '{secret_name}'")
