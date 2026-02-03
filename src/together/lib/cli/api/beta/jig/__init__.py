"""Jig CLI - deployment tool for Together AI."""

import click

from together.lib.cli.api.beta.jig.jig import (
    init,
    logs,
    push,
    build,
    deploy,
    status,
    submit,
    destroy,
    endpoint,
    dockerfile,
    job_status,
    queue_status,
    list_deployments,
)
from together.lib.cli.api.beta.jig.secrets import secrets
from together.lib.cli.api.beta.jig.volumes import volumes


@click.group()
@click.pass_context
def jig(ctx: click.Context) -> None:
    """Jig commands - deploy and manage containers"""
    pass


def add_commands(parent: click.Group) -> None:
    # Add subgroups
    parent.add_command(secrets)
    parent.add_command(volumes)

    # Add main commands
    parent.add_command(init)
    parent.add_command(dockerfile)
    parent.add_command(build)
    parent.add_command(push)
    parent.add_command(deploy)
    parent.add_command(status)
    parent.add_command(endpoint)
    parent.add_command(logs)
    parent.add_command(destroy)
    parent.add_command(submit)
    parent.add_command(job_status)
    parent.add_command(queue_status)
    parent.add_command(list_deployments)


add_commands(jig)
