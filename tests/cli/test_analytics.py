"""CLI tests for telemetry / analytics subcommands and config."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from together.lib.cli import main


@pytest.fixture
def isolated_cli_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """Avoid touching the developer's real ~/.config/together/cli.json."""
    cfg_root = tmp_path / "xdg"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(cfg_root))
    monkeypatch.delenv("TOGETHER_TELEMETRY_DISABLED", raising=False)
    return cfg_root / "together" / "cli.json"


def test_telemetry_disable_then_status(isolated_cli_config: Path) -> None:
    runner = CliRunner()
    r = runner.invoke(main, ["telemetry", "disable"], catch_exceptions=False)
    assert r.exit_code == 0
    assert "Telemetry disabled" in r.output
    assert isolated_cli_config.is_file()
    assert json.loads(isolated_cli_config.read_text(encoding="utf-8"))["telemetry_enabled"] is False

    r2 = runner.invoke(main, ["telemetry", "status"], catch_exceptions=False)
    assert r2.exit_code == 0
    assert "Disabled" in r2.output
    assert "environment variable" not in r2.output.lower()


def test_telemetry_enable_then_status(isolated_cli_config: Path) -> None:
    isolated_cli_config.parent.mkdir(parents=True, exist_ok=True)
    isolated_cli_config.write_text(json.dumps({"telemetry_enabled": False}), encoding="utf-8")

    runner = CliRunner()
    r = runner.invoke(main, ["telemetry", "enable"], catch_exceptions=False)
    assert r.exit_code == 0
    assert "Telemetry enabled" in r.output
    assert json.loads(isolated_cli_config.read_text(encoding="utf-8"))["telemetry_enabled"] is True

    r2 = runner.invoke(main, ["telemetry", "status"], catch_exceptions=False)
    assert r2.exit_code == 0
    assert "Enabled" in r2.output


def test_telemetry_status_shows_env_opt_out(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TOGETHER_TELEMETRY_DISABLED", "1")
    runner = CliRunner()
    r = runner.invoke(main, ["telemetry", "status"], catch_exceptions=False)
    assert r.exit_code == 0
    assert "Disabled" in r.output
    assert "environment variable" in r.output.lower()
