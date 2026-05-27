"""CLI integration: ``track_cli`` is invoked for command lifecycle (start / complete / fail)."""

from __future__ import annotations

import sys
from typing import Any, Generator
from pathlib import Path

import pytest
from cyclopts.command_spec import CommandSpec

from tests.cli.utils import CliRunner
from together.lib.cli import app as tg_app
from together.lib.cli._track_cli import CliTrackingEvents


def _reset_telemetry_command_specs() -> None:
    """Cyclopts caches lazy imports on ``CommandSpec``; clear so ``monkeypatch`` on handlers applies."""
    telemetry = tg_app._commands["telemetry"]
    for cmd in telemetry._commands.values():  # type: ignore
        if isinstance(cmd, CommandSpec):
            cmd._resolved = None


@pytest.fixture(autouse=True)
def reset_telemetry_command_specs_after_each_test() -> Generator[None, Any, None]:
    _reset_telemetry_command_specs()
    yield
    _reset_telemetry_command_specs()


@pytest.fixture
def isolated_cli_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    cfg_root = tmp_path / "xdg"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(cfg_root))
    monkeypatch.delenv("TOGETHER_TELEMETRY_DISABLED", raising=False)
    return cfg_root / "together" / "cli.json"


@pytest.fixture
def track_cli_capture(
    monkeypatch: pytest.MonkeyPatch,
) -> list[tuple[CliTrackingEvents, dict[str, Any]]]:
    captured: list[tuple[CliTrackingEvents, dict[str, Any]]] = []

    def _spy(event: CliTrackingEvents, args: dict[str, Any]) -> None:
        captured.append((event, args))

    monkeypatch.setattr("together.lib.cli.track_cli", _spy)
    return captured


def _event_kinds(captured: list[tuple[CliTrackingEvents, dict[str, Any]]]) -> list[str]:
    return [e.value for e, _ in captured]


@pytest.mark.usefixtures("isolated_cli_config")
def test_command_success_emits_started_then_completed(
    track_cli_capture: list[tuple[CliTrackingEvents, dict[str, Any]]],
    cli_runner: CliRunner,
) -> None:
    r = cli_runner.invoke(["telemetry", "status"])
    assert r.exit_code == 0
    assert _event_kinds(track_cli_capture) == [
        CliTrackingEvents.CommandStarted.value,
        CliTrackingEvents.CommandCompleted.value,
    ]
    for _, payload in track_cli_capture:
        assert payload["command"] == "telemetry status"
        assert payload["is_beta_command"] is False


@pytest.mark.usefixtures("isolated_cli_config")
def test_command_system_exit_failure_emits_started_then_failed(
    track_cli_capture: list[tuple[CliTrackingEvents, dict[str, Any]]],
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _exit_1() -> None:
        sys.exit(1)

    monkeypatch.setattr("together.lib.cli.api.telemetry.status.status", _exit_1)
    r = cli_runner.invoke(["telemetry", "status"])
    assert r.exit_code == 1
    assert _event_kinds(track_cli_capture) == [
        CliTrackingEvents.CommandStarted.value,
        CliTrackingEvents.CommandFailed.value,
    ]
    failed = track_cli_capture[1][1]
    assert failed["command"] == "telemetry status"
    assert "error" in failed


@pytest.mark.usefixtures("isolated_cli_config")
def test_command_system_exit_zero_emits_started_then_completed(
    track_cli_capture: list[tuple[CliTrackingEvents, dict[str, Any]]],
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _exit_0() -> None:
        sys.exit(0)

    monkeypatch.setattr("together.lib.cli.api.telemetry.status.status", _exit_0)
    r = cli_runner.invoke(["telemetry", "status"])
    assert r.exit_code == 0
    assert _event_kinds(track_cli_capture) == [
        CliTrackingEvents.CommandStarted.value,
        CliTrackingEvents.CommandCompleted.value,
    ]


@pytest.mark.usefixtures("isolated_cli_config")
def test_command_exception_emits_started_then_failed_then_reraises(
    track_cli_capture: list[tuple[CliTrackingEvents, dict[str, Any]]],
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _boom() -> None:
        raise RuntimeError("something broke")

    monkeypatch.setattr("together.lib.cli.api.telemetry.status.status", _boom)
    cli_runner.invoke(["telemetry", "status"])

    assert _event_kinds(track_cli_capture) == [
        CliTrackingEvents.CommandStarted.value,
        CliTrackingEvents.CommandFailed.value,
    ]
    err = track_cli_capture[1][1]["error"]
    assert "something broke" in err


@pytest.mark.usefixtures("isolated_cli_config")
def test_command_keyboard_interrupt_emits_started_then_user_aborted(
    track_cli_capture: list[tuple[CliTrackingEvents, dict[str, Any]]],
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _interrupt() -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr("together.lib.cli.api.telemetry.status.status", _interrupt)
    r = cli_runner.invoke(["telemetry", "status"])
    assert r.exit_code == 0
    assert _event_kinds(track_cli_capture) == [
        CliTrackingEvents.CommandStarted.value,
        CliTrackingEvents.CommandUserAborted.value,
    ]
