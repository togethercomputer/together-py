"""Legacy Click-based Jig CLI - invoked when using together beta jig <subcommand>."""

import sys

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


jig.add_command(secrets)
jig.add_command(volumes)
jig.add_command(init)
jig.add_command(dockerfile)
jig.add_command(build)
jig.add_command(push)
jig.add_command(deploy)
jig.add_command(status)
jig.add_command(endpoint)
jig.add_command(logs)
jig.add_command(destroy)
jig.add_command(submit)
jig.add_command(job_status)
jig.add_command(queue_status)
jig.add_command(list_deployments, name="list")


def main(argv: list[str] | None = None, obj: object = None) -> None:
    """Run the Click-based Jig CLI. obj is passed as ctx.obj (e.g. Together client)."""
    if argv is None:
        argv = sys.argv[1:]
    jig.main(args=argv, prog_name="together beta jig", standalone_mode=True, obj=obj)
