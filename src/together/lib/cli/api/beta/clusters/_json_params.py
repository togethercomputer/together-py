from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def parse_json_object(value: str, parameter_name: str) -> dict[str, Any]:
    parsed = _parse_json(value, parameter_name)
    if not isinstance(parsed, dict):
        raise ValueError(f"{parameter_name} must be a JSON object")
    return parsed


def parse_json_array(value: str, parameter_name: str) -> list[Any]:
    parsed = _parse_json(value, parameter_name)
    if not isinstance(parsed, list):
        raise ValueError(f"{parameter_name} must be a JSON array")
    return parsed


def _parse_json(value: str, parameter_name: str) -> Any:
    if value.startswith("@"):
        value = Path(value[1:]).read_text()
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{parameter_name} must be valid JSON") from exc
