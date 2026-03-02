from __future__ import annotations

import sys
from typing import Annotated
from pathlib import Path

from rich import print, print_json
from cyclopts import Parameter

from together.lib.utils import check_file
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfig


async def check(
    file: Annotated[Path, Parameter(required=True, help="The file to check")],
    *,
    config: Annotated[CLIConfig, Parameter(parse=False)],
) -> None:
    """Check file for issues"""

    report = check_file(file)

    if config.json:
        print_json(openapi_dumps(report).decode("utf-8"))
    else:
        icon = "✅" if report["is_check_passed"] else "❌"
        print(f"{icon} {report['message']}")
        if report["is_check_passed"] is False:
            sys.exit(1)
