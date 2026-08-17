from __future__ import annotations

import sys
from typing import Annotated
from pathlib import Path

from cyclopts import Parameter
from rich.markup import escape as escape_rich_markup

from together.lib.utils import check_file
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.check_progress import CheckProgressTracker, should_show_check_progress


async def check(
    file: Annotated[Path, Parameter(required=True, help="The file to check")],
    *,
    config: CLIConfigParameter,
) -> None:
    """Check file for issues"""

    with CheckProgressTracker(file, enabled=should_show_check_progress(file, json_mode=config.json)) as tracker:
        report = check_file(file, progress_callback=tracker.as_callback())

    if config.json:
        console.print_json(openapi_dumps(report).decode("utf-8"))
    else:
        status = "[green]OK[/green]" if report["is_check_passed"] else "[red]X[/red]"
        console.print(f"{status} {escape_rich_markup(str(report['message']))}")
        if report["is_check_passed"] is False:
            sys.exit(1)
