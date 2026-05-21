from __future__ import annotations

import json
from typing import Any, cast
from pathlib import Path


def parse_json_object(value: str, parameter_name: str) -> dict[str, Any]:
    parsed = _parse_json(value, parameter_name)
    if not isinstance(parsed, dict):
        raise ValueError(f"{parameter_name} must be a JSON object")
    return cast(dict[str, Any], parsed)


def parse_json_array(value: str, parameter_name: str) -> list[Any]:
    parsed = _parse_json(value, parameter_name)
    if not isinstance(parsed, list):
        raise ValueError(f"{parameter_name} must be a JSON array")
    return cast(list[Any], parsed)


def _parse_json(value: str, parameter_name: str) -> Any:
    if value.startswith("@"):
        value = Path(value[1:]).read_text()
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{parameter_name} must be valid JSON") from exc
