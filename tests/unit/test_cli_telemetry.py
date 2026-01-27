from __future__ import annotations

import json
from pathlib import Path

import pytest

from together.lib.cli._track_cli import (
    is_tracking_enabled,
    load_telemetry_config,
    save_telemetry_config,
    telemetry_config_path,
    _sanitize_cli_error_message,
)


@pytest.fixture(autouse=True)
def _xdg_config_home(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:  # type: ignore
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg_config"))


def test_sanitize_cli_error_message_truncates() -> None:
    long = "a" * 600
    out = _sanitize_cli_error_message(long)
    assert len(out) < len(long)
    assert out.endswith("…")


def test_sanitize_cli_error_message_redacts_bearer() -> None:
    msg = "failed: bearer abcdefghijklmnopqrstuvwxyz0123456789"
    assert "abcdefghij" not in _sanitize_cli_error_message(msg)


def test_telemetry_env_opt_out_only_explicit_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TOGETHER_TELEMETRY_DISABLED", raising=False)
    assert is_tracking_enabled() is True
    monkeypatch.setenv("TOGETHER_TELEMETRY_DISABLED", "0")
    assert is_tracking_enabled() is True
    monkeypatch.setenv("TOGETHER_TELEMETRY_DISABLED", "1")
    assert is_tracking_enabled() is False
    monkeypatch.setenv("TOGETHER_TELEMETRY_DISABLED", "TRUE")
    assert is_tracking_enabled() is False
    monkeypatch.setenv("TOGETHER_TELEMETRY_DISABLED", " yes ")
    assert is_tracking_enabled() is False


def test_telemetry_config_file_disables(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("TOGETHER_TELEMETRY_DISABLED", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))
    path = tmp_path / "cfg" / "together" / "cli.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"telemetry_enabled": False}), encoding="utf-8")
    assert is_tracking_enabled() is False


def test_save_and_load_roundtrip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TOGETHER_TELEMETRY_DISABLED", raising=False)
    save_telemetry_config({"telemetry_enabled": True, "telemetry_notice_shown": True})
    assert load_telemetry_config() == {"telemetry_enabled": True, "telemetry_notice_shown": True}
    assert telemetry_config_path().is_file()


def test_together_telemetry_status_no_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
    monkeypatch.delenv("TOGETHER_TELEMETRY_DISABLED", raising=False)
    from click.testing import CliRunner

    from together.lib.cli import main

    runner = CliRunner()
    result = runner.invoke(main, ["telemetry", "status"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "Telemetry:" in result.output
