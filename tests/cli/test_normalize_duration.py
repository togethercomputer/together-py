from __future__ import annotations

import pytest

from together.lib.cli.api.beta.endpoints._utils._duration import normalize_duration


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, None),
        ("30s", "30s"),
        (" 30s ", "30s"),
        ("180s", "180s"),
        ("390s", "390s"),
        ("1.5s", "1.5s"),
        ("0s", "0s"),
        ("-30s", "-30s"),
        ("30", "30s"),
        ("10", "10s"),
        ("10m", "600s"),
        ("2m", "120s"),
        ("1h", "3600s"),
        ("10m30s", "630s"),
        ("1ms", "0.001s"),
        ("5m", "300s"),
        ("1.5m", "90s"),
        ("-10m", "-600s"),
        ("3m0s", "180s"),
    ],
)
def test_normalize_duration_accepts(value: str | None, expected: str | None) -> None:
    assert normalize_duration(value, option_name="--interval") == expected


@pytest.mark.parametrize(
    "value",
    ["", "   ", "10m30", "30S", "PT1M", "abc", "1 hour", "10M", "+30s", "1d"],
)
def test_normalize_duration_rejects(value: str, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        normalize_duration(value, option_name="--interval")
    output = capsys.readouterr().out
    assert "--interval must be a duration, e.g. 30, 30s, or 10m" in output
    assert f"(got {value.strip()!r})" in output
