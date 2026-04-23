from __future__ import annotations

import json
import urllib.request
from typing import Any
from pathlib import Path

import pytest

from tests.cli.utils import CliRunner
from together.lib.cli._track_cli import (
    CliTrackingEvents,
    track_cli,
    is_tracking_enabled,
    load_telemetry_config,
    save_telemetry_config,
    telemetry_config_path,
    sanitize_cli_error_message,
)


@pytest.fixture(autouse=True)
def _xdg_config_home(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:  # type: ignore
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg_config"))


def test_sanitize_cli_error_message_truncates() -> None:
    long = "a" * 600
    out = sanitize_cli_error_message(long)
    assert len(out) < len(long)
    assert out.endswith("…")


def test_sanitize_cli_error_message_redacts_bearer() -> None:
    msg = "failed: bearer abcdefghijklmnopqrstuvwxyz0123456789"
    assert "abcdefghij" not in sanitize_cli_error_message(msg)


def test_sanitize_cli_error_message_redacts_authorization_header() -> None:
    msg = "oops Authorization: supersecrettokenvaluehere"
    out = sanitize_cli_error_message(msg)
    assert "supersecret" not in out
    assert "<redacted>" in out


def test_sanitize_cli_error_message_redacts_api_key_assignment() -> None:
    # Pattern matches ``api_key`` + whitespace + long token (not ``key="..."``).
    msg = "config api_key sk-abcdefghijklmnopqrstuvwxyz0123456789"
    out = sanitize_cli_error_message(msg)
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

    def _urlopen_should_not_run(*_a: Any, **_kw: Any) -> Any:
        raise AssertionError("urllib.request.urlopen must not be used when telemetry is off")

    monkeypatch.setattr("together.lib.cli._track_cli.urllib.request.urlopen", _urlopen_should_not_run)
    track_cli(CliTrackingEvents.CommandStarted, {"command": "x", "arguments": []})


def test_track_cli_posts_json_when_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TOGETHER_TELEMETRY_DISABLED", raising=False)
    posted: list[urllib.request.Request] = []

    class _FakeResponse:
        status = 200

        def __enter__(self) -> _FakeResponse:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self, _n: int = -1) -> bytes:
            return b""

    def _urlopen_fake(
        req: urllib.request.Request,
        _data: object = None,
        timeout: object = None,
        **_kw: object,
    ) -> _FakeResponse:
        del timeout  # use var name to avoid lint error
        posted.append(req)
        return _FakeResponse()

    monkeypatch.setattr("together.lib.cli._track_cli.urllib.request.urlopen", _urlopen_fake)
    monkeypatch.setenv(
        "TOGETHER_TELEMETRY_API",
        "https://example.test/telemetry",
    )

    t = track_cli(
        CliTrackingEvents.CommandCompleted,
        {"command": "models list", "arguments": ["json"]},
    )
    assert t is not None
    t.join(timeout=5.0)
    assert len(posted) == 1
    req = posted[0]
    assert req.get_full_url() == "https://example.test/telemetry"
    payload = req.data
    assert isinstance(payload, bytes)
    body = json.loads(payload.decode("utf-8"))
    assert body["event_type"] == "cli_command_completed"
    assert body["event_properties"]["command"] == "models list"
    assert body["event_properties"]["arguments"] == ["json"]
    assert body["context"]["runtime"]["name"] == "together-cli"


def test_parse_command_and_flags_splits_command_and_flags() -> None:
    from together.lib.cli import app
    from together.lib.cli._track_cli import parse_command_and_flags

    cmd, flags, is_beta = parse_command_and_flags(app, ["files", "upload", "--file", "ignored.txt"])
    assert cmd == "files upload"
    assert flags == ["file"]
    assert is_beta is False


def test_parse_command_and_flags_strips_beta_prefix() -> None:
    from together.lib.cli import app
    from together.lib.cli._track_cli import parse_command_and_flags

    cmd, flags, is_beta = parse_command_and_flags(app, ["beta", "clusters", "list"])
    assert cmd == "clusters list"
    assert flags == []
    assert is_beta is True


def test_parse_command_and_flags_positionals_are_argument_names_not_command_tokens() -> None:
    from together.lib.cli import app
    from together.lib.cli._track_cli import parse_command_and_flags

    cmd, flags, is_beta = parse_command_and_flags(app, ["beta", "jig", "secrets", "set", "secret-name", "secret-value"])
    assert cmd == "jig secrets set"
    assert set(flags) == {"name", "value"}
    assert is_beta is True


def test_telemetry_status_no_api_key(monkeypatch: pytest.MonkeyPatch, cli_runner: CliRunner) -> None:
    monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
    monkeypatch.delenv("TOGETHER_TELEMETRY_DISABLED", raising=False)
    monkeypatch.setenv("TOGETHER_BASE_URL", "http://127.0.0.1:4010")

    result = cli_runner.invoke(["telemetry", "status"])
    assert result.exit_code == 0
    assert "Telemetry:" in result.output
