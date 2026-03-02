from __future__ import annotations

import json
from pathlib import Path

from together.lib.utils import check_file


def check(file: Path) -> None:
    """Check file for issues."""
    report = check_file(file)
    print(json.dumps(report, indent=4))
