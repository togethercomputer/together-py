"""Secrets management CLI commands for jig."""

from __future__ import annotations

import click

from together import Together
from together._exceptions import APIStatusError
from together.lib.cli.api._utils import handle_api_errors
from together.lib.cli.api.beta.jig._config import State, Config


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
@click.option("-c", "--config", "config_path", default=None, help="Configuration file path")
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
    state = State.load(config._path.parent, config.model_name)

    deployment_secret_name = f"{config.model_name}-{name}"

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
    except APIStatusError as e:
        if hasattr(e, "status_code") and e.status_code == 404:
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
@click.option("-c", "--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Secrets")
def secrets_unset(
    ctx: click.Context,  # noqa: ARG001
    name: str,
    config_path: str | None,
) -> None:
    """Remove a secret from both remote and local state"""
    config = Config.find(config_path)
    state = State.load(config._path.parent, config.model_name)

    if state.secrets.pop(name, ""):
        state.save()
        click.echo(f"\N{CHECK MARK} Deleted secret '{name}' from local state")
    else:
        click.echo(f"\N{CROSS MARK} Secret '{name}' is not set")


@secrets.command("list")
@click.pass_context
@click.option("-c", "--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Secrets")
def secrets_list(
    ctx: click.Context,
    config_path: str | None,
) -> None:
    """List all secrets with sync status"""
    client: Together = ctx.obj
    config = Config.find(config_path)
    state = State.load(config._path.parent, config.model_name)

    prefix = f"{config.model_name}-"

    # Get remote secrets for this deployment
    remote_response = client.beta.jig.secrets.list()
    remote_secrets: set[str] = set()

    if hasattr(remote_response, "data") and remote_response.data:
        for secret in remote_response.data:
            secret_name = getattr(secret, "name", None)
            if secret_name and secret_name.startswith(prefix):
                # Strip prefix to get local name
                remote_secrets.add(secret_name[len(prefix) :])

    # Get local secrets
    local_secrets = set(state.secrets.keys())

    # Combine all secrets
    all_secrets = local_secrets | remote_secrets

    if not all_secrets:
        click.echo(f"\N{INFORMATION SOURCE} No secrets configured for deployment '{config.model_name}'")
        return

    click.echo(f"\N{INFORMATION SOURCE} Secrets for deployment '{config.model_name}':")
    click.echo()

    for name in sorted(all_secrets):
        in_local = name in local_secrets
        in_remote = name in remote_secrets

        if in_local and in_remote:
            status = click.style("synced", fg="green")
        elif in_local and not in_remote:
            status = click.style("local only", fg="yellow")
        else:  # in_remote and not in_local
            status = click.style("remote only", fg="yellow")

        click.echo(f"  - {name} [{status}]")
