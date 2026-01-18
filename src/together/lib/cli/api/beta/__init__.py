import click

from together.lib.cli.api.beta.clusters import clusters


@click.group()
def beta() -> None:
    """Beta API commands"""
    pass


beta.add_command(clusters)
