"""CLI tests for telemetry / analytics subcommands and config."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tests.cli.utils import CliRunner


@pytest.fixture
def isolated_cli_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """Avoid touching the developer's real ~/.config/together/cli.json."""
    cfg_root = tmp_path / "xdg"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(cfg_root))
    monkeypatch.delenv("TOGETHER_TELEMETRY_DISABLED", raising=False)
    return cfg_root / "together" / "cli.json"


def test_telemetry_disable_then_status(isolated_cli_config: Path, cli_runner: CliRunner) -> None:
    r = cli_runner.invoke(["telemetry", "disable"])
    assert r.exit_code == 0
    assert "Telemetry: Disabled" in r.output
    assert isolated_cli_config.is_file()
    assert json.loads(isolated_cli_config.read_text(encoding="utf-8"))["telemetry_enabled"] is False

    r2 = cli_runner.invoke(["telemetry", "status"])
    assert r2.exit_code == 0
    assert "Disabled" in r2.output
    assert "environment variable" not in r2.output.lower()


def test_telemetry_enable_then_status(isolated_cli_config: Path, cli_runner: CliRunner) -> None:
    isolated_cli_config.parent.mkdir(parents=True, exist_ok=True)
    isolated_cli_config.write_text(json.dumps({"telemetry_enabled": False}), encoding="utf-8")

    r = cli_runner.invoke(["telemetry", "enable"])
    assert r.exit_code == 0
    assert "Telemetry: Enabled" in r.output
    assert json.loads(isolated_cli_config.read_text(encoding="utf-8"))["telemetry_enabled"] is True

    r2 = cli_runner.invoke(["telemetry", "status"])
    assert r2.exit_code == 0
    assert "Enabled" in r2.output


def test_telemetry_json_mode_pipes_to_jq(cli_runner: CliRunner) -> None:
    r = cli_runner.invoke(["telemetry", "status", "--json"])
    assert r.exit_code == 0
    jq = subprocess.run(["jq"], input=r.out_out, capture_output=True, text=True)
    assert jq.returncode == 0, jq.stderr


def test_telemetry_status_shows_env_opt_out(
    isolated_cli_config: Path,
    monkeypatch: pytest.MonkeyPatch,
    cli_runner: CliRunner,
) -> None:
    """Without XDG isolation, a real cli.json can disable telemetry before env is considered."""
    assert not isolated_cli_config.exists()
    monkeypatch.setenv("TOGETHER_TELEMETRY_DISABLED", "1")
    r = cli_runner.invoke(["telemetry", "status"])
    assert r.exit_code == 0
    assert "Disabled" in r.output
    assert "environment variable" in r.output.lower()
