"""Secrets management CLI commands for jig."""

from __future__ import annotations

import click
from rich.pretty import pprint

from together import Together
from together.lib.cli.api._utils import handle_api_errors

from ._config import Config, State


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
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Secrets")
def secrets_set(
    ctx: click.Context,
    name: str,
    value: str,
    description: str,
    config_path: str | None,
) -> None:
    """Set a secret (create or update)"""
    client: Together = ctx.obj
    config = Config.find(config_path)
    state = State.load(config._path.parent)

    deployment_secret_name = f"{config.model_name}-{name}"
    secret_data = {
        "name": deployment_secret_name,
        "description": description,
        "value": value,
    }

    # Try to get existing secret to determine if we should update
    try:
        client.beta.jig.secrets.retrieve(deployment_secret_name)
        # Secret exists, update it
        client.beta.jig.secrets.update(
            deployment_secret_name,
            name=deployment_secret_name,
            description=description,
            value=value,
        )
        click.echo(f"\N{CHECK MARK} Updated secret: '{name}'")
    except Exception as e:
        # Check if it's a 404
        if hasattr(e, "status_code") and e.status_code == 404:
            # Secret doesn't exist, create it
            click.echo("\N{ROCKET} Creating new secret")
            client.beta.jig.secrets.create(
                name=deployment_secret_name,
                value=value,
                description=description,
            )
            click.echo(f"\N{CHECK MARK} Created secret: {name}")
        else:
            raise

    state.secrets[name] = deployment_secret_name
    state.save()


@secrets.command("unset")
@click.pass_context
@click.option("--name", required=True, help="Secret name to remove")
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Secrets")
def secrets_unset(
    ctx: click.Context,
    name: str,
    config_path: str | None,
) -> None:
    """Remove a secret from deployment configuration"""
    config = Config.find(config_path)
    state = State.load(config._path.parent)

    if state.secrets.pop(name, ""):
        state.save()
        click.echo("\N{CHECK MARK} Removed secret from deployment")
    else:
        click.echo(f"Secret {name} is not set")


@secrets.command("list")
@click.pass_context
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Secrets")
def secrets_list(
    ctx: click.Context,
    config_path: str | None,
) -> None:
    """List all secrets configured for deployment"""
    config = Config.find(config_path)
    state = State.load(config._path.parent)

    msg = f"\N{INFORMATION SOURCE} Following secrets are mapped to deployment {config.model_name}"
    click.echo(msg)
    for secret_name in state.secrets:
        click.echo(f"  - Secret '{secret_name}'")


@secrets.command("list-all")
@click.pass_context
@handle_api_errors("Secrets")
def secrets_list_all(ctx: click.Context) -> None:
    """List all secrets in the project"""
    client: Together = ctx.obj
    response = client.beta.jig.secrets.list()
    pprint(response.model_dump() if hasattr(response, "model_dump") else response, indent_guides=False)


@secrets.command("delete")
@click.pass_context
@click.option("--name", required=True, help="Secret name to delete from server")
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Secrets")
def secrets_delete(
    ctx: click.Context,
    name: str,
    config_path: str | None,
) -> None:
    """Delete a secret from the server"""
    client: Together = ctx.obj
    config = Config.find(config_path)
    state = State.load(config._path.parent)

    deployment_secret_name = f"{config.model_name}-{name}"

    try:
        client.beta.jig.secrets.delete(deployment_secret_name)
        click.echo(f"\N{CHECK MARK} Deleted secret '{name}'")
    except Exception as e:
        if hasattr(e, "status_code") and e.status_code == 404:
            click.echo(f"\N{CROSS MARK} Secret '{name}' not found")
            return
        raise

    # Also remove from local state
    if name in state.secrets:
        del state.secrets[name]
        state.save()
