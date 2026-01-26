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
    """Jig API commands - deployment tool for Together AI"""
    pass


# Add subgroups
jig.add_command(secrets)
jig.add_command(volumes)

# Add main commands
jig.add_command(init)
jig.add_command(dockerfile)
jig.add_command(build)
jig.add_command(push)
jig.add_command(deploy)
jig.add_command(status)
jig.add_command(logs)
jig.add_command(destroy)
jig.add_command(submit)
jig.add_command(job_status)
jig.add_command(queue_status)
jig.add_command(list_deployments)
