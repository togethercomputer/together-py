import sys
import json as json_lib
import pathlib

import click
from rich import print, print_json

from together.lib.utils import check_file
from together.lib.cli._track_cli import auto_track_command


@click.command()
@click.pass_context
@click.argument(
    "file",
    type=click.Path(exists=True, file_okay=True, resolve_path=True, readable=True, dir_okay=False),
    required=True,
)
@click.option(
    "--json",
    is_flag=True,
    help="Output the response in JSON format",
)
@auto_track_command
def check(_ctx: click.Context, file: pathlib.Path, json: bool) -> None:
    """Check file for issues"""

    report = check_file(file)

    if json:
        print_json(json_lib.dumps(report))
    else:
        icon = "✅" if report["is_check_passed"] else "❌"
        print(f"{icon} {report['message']}")
        if report["is_check_passed"] is False:
            sys.exit(1)
