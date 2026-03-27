from __future__ import annotations

import json
from typing import Any
from pathlib import Path

import click
import pytest
from click.testing import CliRunner

from together.lib.cli._track_cli import (
    CliTrackingEvents,
    track_cli,
    auto_track_command,
    is_tracking_enabled,
    load_telemetry_config,
    save_telemetry_config,
    telemetry_config_path,
    invoked_subcommand_path,
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


def test_sanitize_cli_error_message_redacts_authorization_header() -> None:
    msg = "oops Authorization: supersecrettokenvaluehere"
    out = _sanitize_cli_error_message(msg)
    assert "supersecret" not in out
    assert "<redacted>" in out


def test_sanitize_cli_error_message_redacts_api_key_assignment() -> None:
    # Pattern matches ``api_key`` + whitespace + long token (not ``key="..."``).
    msg = "config api_key sk-abcdefghijklmnopqrstuvwxyz0123456789"
    out = _sanitize_cli_error_message(msg)
    assert "sk-abc" not in out
    assert "<redacted>" in out


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


def test_load_telemetry_config_invalid_json_returns_empty(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    path = tmp_path / "xdg" / "together" / "cli.json"
    path.parent.mkdir(parents=True)
    path.write_text("{not json", encoding="utf-8")
    assert load_telemetry_config() == {}


def test_track_cli_skips_http_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TOGETHER_TELEMETRY_DISABLED", "1")

    def _client_should_not_run(**_kw: Any) -> Any:
        raise AssertionError("httpx.Client must not be used when telemetry is off")

    monkeypatch.setattr("together.lib.cli._track_cli.httpx.Client", _client_should_not_run)
    track_cli(CliTrackingEvents.CommandStarted, {"command": "x", "arguments": []})


def test_track_cli_posts_json_when_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TOGETHER_TELEMETRY_DISABLED", raising=False)
    posted: list[tuple[str, dict[str, Any]]] = []

    class _Client:
        def __enter__(self) -> _Client:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def post(self, url: str, **kwargs: Any) -> None:
            posted.append((url, kwargs))

    def _client_factory(**_kw: Any) -> _Client:
        return _Client()

    monkeypatch.setattr("together.lib.cli._track_cli.httpx.Client", _client_factory)
    monkeypatch.setenv(
        "TOGETHER_TELEMETRY_API",
        "https://example.test/telemetry",
    )

    track_cli(
        CliTrackingEvents.CommandCompleted,
        {"command": "models list", "arguments": ["json"]},
    )
    assert len(posted) == 1
    url, kw = posted[0]
    assert url == "https://example.test/telemetry"
    body = json.loads(str(kw["content"]))
    assert body["event_type"] == "cli_command_completed"
    assert body["event_properties"]["command"] == "models list"
    assert body["event_properties"]["arguments"] == ["json"]
    assert body["context"]["runtime"]["name"] == "together-cli"


def test_auto_track_command_records_failure_with_sanitized_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[tuple[str, dict[str, Any]]] = []

    def capture(ev: CliTrackingEvents, args: dict[str, Any]) -> None:
        events.append((ev.value, args))

    monkeypatch.setattr("together.lib.cli._track_cli.track_cli", capture)

    @click.group("cli")
    def root() -> None:
        pass

    @root.command("fail")
    @auto_track_command
    def _fail_cmd() -> None:  # pyright: ignore[reportUnusedFunction]
        raise RuntimeError("bearer abcdefghijklmnopqrstuvwxyz0123456789")

    runner = CliRunner()
    r = runner.invoke(root, ["fail"], catch_exceptions=True)
    assert r.exit_code != 0
    kinds = [e[0] for e in events]
    assert kinds == [
        "cli_command_started",
        "cli_command_failed",
    ]
    err = events[1][1]["error"]
    assert "abcdefghij" not in err
    assert "<redacted>" in err


def test_invoked_subcommand_path_strips_root_name() -> None:
    @click.group("together")
    def root() -> None:
        pass

    @root.group("models")
    def models_g() -> None:
        pass

    @models_g.group("list")
    def list_g() -> None:
        pass

    @list_g.command("all")
    def _all_cmd() -> None:  # pyright: ignore[reportUnusedFunction]
        click.echo(invoked_subcommand_path())

    runner = CliRunner()
    r = runner.invoke(root, ["models", "list", "all"], catch_exceptions=False)
    assert r.exit_code == 0
    assert r.output.strip() == "models list all"


def test_together_telemetry_status_no_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
    monkeypatch.delenv("TOGETHER_TELEMETRY_DISABLED", raising=False)
    from together.lib.cli import main

    runner = CliRunner()
    result = runner.invoke(main, ["telemetry", "status"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "Telemetry:" in result.output
