import json
import pathlib
from typing import Any, List
from textwrap import wrap

import click
from tabulate import tabulate

from together import Together

from ...utils import check_file, convert_bytes, convert_unix_timestamp


@click.group()
@click.pass_context
def files(_ctx: click.Context) -> None:
    """File API commands"""
    pass


# TODO: Implement upload command
@files.command()
@click.pass_context
@click.argument(
    "file",
    type=click.Path(exists=True, file_okay=True, resolve_path=True, readable=True, dir_okay=False),
    required=True,
)
@click.option(
    "--purpose",
    type=str,
    default="fine-tunes",
    help="Purpose of file upload. Acceptable values in enum `together.types.FilePurpose`. Defaults to `fine-tunes`.",
)
@click.option(
    "--check/--no-check",
    default=True,
    help="Whether to check the file before uploading.",
)
def upload(_ctx: click.Context, _file: pathlib.Path, _purpose: str, _check: bool) -> None:
    """Upload file"""

    # the file upload API is not implemented yet
    raise NotImplementedError

    # client: Together = ctx.obj

    # response = client.files.upload(file=file, purpose=purpose, check=check)

    # click.echo(json.dumps(response.model_dump(), indent=4))


@files.command()
@click.pass_context
def list(ctx: click.Context) -> None:
    """List files"""
    client: Together = ctx.obj

    response = client.files.list()

    display_list: List[dict[str, Any]] = []
    for i in response.data or []:
        display_list.append(
            {
                "File name": "\n".join(wrap(i.filename or "", width=30)),
                "File ID": i.id,
                "Size": convert_bytes(float(str(i.bytes))),  # convert to string for mypy typing
                "Created At": convert_unix_timestamp(i.created_at or 0),
                "Line Count": i.line_count,
            }
        )
    table = tabulate(display_list, headers="keys", tablefmt="grid", showindex=True)

    click.echo(table)


@files.command()
@click.pass_context
@click.argument("id", type=str, required=True)
def retrieve(ctx: click.Context, id: str) -> None:
    """Upload file"""

    client: Together = ctx.obj

    response = client.files.retrieve(id=id)

    click.echo(json.dumps(response.model_dump(), indent=4))


@files.command()
@click.pass_context
@click.argument("id", type=str, required=True)
@click.option("--output", type=str, default=None, help="Output filename")
def retrieve_content(ctx: click.Context, id: str, output_path: str) -> None:
    """Retrieve file content and output to file"""

    client: Together = ctx.obj

    response = client.files.content(id=id)

    if output_path:
        response.write_to_file(output_path)

    click.echo(json.dumps(response.json, indent=4))


@files.command()
@click.pass_context
@click.argument("id", type=str, required=True)
def delete(ctx: click.Context, id: str) -> None:
    """Delete remote file"""

    client: Together = ctx.obj

    response = client.files.delete(id=id)

    click.echo(json.dumps(response.model_dump(), indent=4))


@files.command()
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
