import json
import pathlib

import click

from together.lib.utils import check_file


@click.command()
@click.pass_context
@click.argument(
    "file",
    type=click.Path(exists=True, file_okay=True, resolve_path=True, readable=True, dir_okay=False),
    required=True,
)
def check(_ctx: click.Context, file: pathlib.Path) -> None:
    """Check file for issues"""

    report = check_file(file)

    click.echo(json.dumps(report, indent=4))
