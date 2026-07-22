from __future__ import annotations

import json
import threading
import subprocess
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from together.lib.cli.utils import _version_check


class _Response:
    def __init__(self, body: bytes):
        self.body = body

    def read(self) -> bytes:
        return self.body

    def __enter__(self) -> _Response:
        return self

    def __exit__(self, *_args: object) -> None:
        pass


@pytest.mark.parametrize(
    ("latest_version", "current_version", "expected"),
    [
        ("2.10.0", "2.9.0", True),
        ("3.0.0", "2.99.99", True),
        ("2.9.1", "2.9.1", False),
        ("2.9.0", "2.9.1", False),
    ],
)
def test_is_newer_version(latest_version: str, current_version: str, expected: bool) -> None:
    assert _version_check._is_newer_version(latest_version, current_version) is expected


def test_parse_version_rejects_non_release_versions() -> None:
    with pytest.raises(ValueError, match="Invalid Together CLI version"):
        _version_check._parse_version("2.9.0rc1")


def test_latest_version_uses_fresh_cache(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cache_path = tmp_path / "version-check.json"
    cache_path.write_text(json.dumps({"checked_at": 1000, "latest_version": "3.1.0"}), encoding="utf-8")
    monkeypatch.setattr(_version_check, "_cache_path", lambda: cache_path)
    monkeypatch.setattr(_version_check.time, "time", lambda: 1001)
    fetch = MagicMock()
    monkeypatch.setattr(_version_check, "_fetch_latest_version", fetch)

    assert _version_check._latest_version() == "3.1.0"
    fetch.assert_not_called()


def test_latest_version_fetches_pypi_and_caches(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cache_path = tmp_path / "cache" / "version-check.json"
    monkeypatch.setattr(_version_check, "_cache_path", lambda: cache_path)
    monkeypatch.setattr(_version_check.time, "time", lambda: 1000)
    urlopen = MagicMock(return_value=_Response(b'{"info":{"version":"3.2.1"}}'))
    monkeypatch.setattr(_version_check.urllib.request, "urlopen", urlopen)

    assert _version_check._latest_version() == "3.2.1"
    assert json.loads(cache_path.read_text(encoding="utf-8")) == {
        "checked_at": 1000,
        "latest_version": "3.2.1",
    }

    request = urlopen.call_args.args[0]
    assert request.full_url == "https://pypi.org/pypi/together/json"
    assert urlopen.call_args.kwargs == {"timeout": 1.0}


async def test_version_check_starts_resolution_when_created(monkeypatch: pytest.MonkeyPatch) -> None:
    started = threading.Event()
    release = threading.Event()

    def latest_version() -> str:
        started.set()
        release.wait()
        return "1.0.0"

    monkeypatch.delenv("TOGETHER_DISABLE_VERSION_CHECK", raising=False)
    monkeypatch.setattr(_version_check, "__version__", "1.0.0")
    monkeypatch.setattr(_version_check, "_latest_version", latest_version)

    version_check = _version_check.VersionCheck()
    try:
        assert started.wait(timeout=1)
    finally:
        release.set()

    await version_check.inform(non_interactive=True, allow_prompt=True)


async def test_disabled_version_check_does_not_start_resolution(monkeypatch: pytest.MonkeyPatch) -> None:
    latest_version = MagicMock()
    monkeypatch.setenv("TOGETHER_DISABLE_VERSION_CHECK", "1")
    monkeypatch.setattr(_version_check, "_latest_version", latest_version)

    version_check = _version_check.VersionCheck()
    await version_check.inform(non_interactive=True, allow_prompt=True)

    latest_version.assert_not_called()


async def test_version_check_stops_waiting_after_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    started = threading.Event()
    release = threading.Event()
    output = MagicMock()

    def latest_version() -> str:
        started.set()
        release.wait()
        return "1.1.0"

    monkeypatch.delenv("TOGETHER_DISABLE_VERSION_CHECK", raising=False)
    monkeypatch.setattr(_version_check, "__version__", "1.0.0")
    monkeypatch.setattr(_version_check, "_latest_version", latest_version)
    monkeypatch.setattr(_version_check, "_RESOLUTION_TIMEOUT_SECONDS", 0.01)
    monkeypatch.setattr(_version_check, "error_console", output)

    version_check = _version_check.VersionCheck()
    assert started.wait(timeout=1)
    try:
        await version_check.inform(non_interactive=True, allow_prompt=True)
    finally:
        release.set()

    output.print.assert_not_called()


async def test_version_check_prints_upgrade_command_when_non_interactive(monkeypatch: pytest.MonkeyPatch) -> None:
    output = MagicMock()
    monkeypatch.delenv("TOGETHER_DISABLE_VERSION_CHECK", raising=False)
    monkeypatch.setattr(_version_check, "__version__", "1.0.0")
    monkeypatch.setattr(_version_check, "_latest_version", lambda: "1.1.0")
    monkeypatch.setattr(
        _version_check, "_upgrade_command", lambda: ["python", "-m", "pip", "install", "-U", "together"]
    )
    monkeypatch.setattr(_version_check, "error_console", output)

    version_check = _version_check.VersionCheck()
    await version_check.inform(non_interactive=True, allow_prompt=True)

    rendered = " ".join(call.args[0] for call in output.print.call_args_list)
    assert "1.0.0 → 1.1.0" in rendered
    assert "python -m pip install -U together" in rendered


async def test_version_check_does_not_prompt_after_failed_command(monkeypatch: pytest.MonkeyPatch) -> None:
    output = MagicMock()
    confirm = AsyncMock()
    monkeypatch.delenv("TOGETHER_DISABLE_VERSION_CHECK", raising=False)
    monkeypatch.setattr(_version_check, "__version__", "1.0.0")
    monkeypatch.setattr(_version_check, "_latest_version", lambda: "1.1.0")
    monkeypatch.setattr(_version_check, "_upgrade_command", lambda: ["upgrade"])
    monkeypatch.setattr(_version_check, "error_console", output)
    monkeypatch.setattr(_version_check, "confirm", confirm)

    version_check = _version_check.VersionCheck()
    await version_check.inform(non_interactive=False, allow_prompt=False)

    confirm.assert_not_awaited()
    assert "Upgrade with:" in output.print.call_args.args[0]


async def test_version_check_prompts_and_upgrades_on_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    output = MagicMock()
    confirm = AsyncMock(return_value=True)
    run = MagicMock(return_value=subprocess.CompletedProcess(["upgrade"], returncode=0))
    monkeypatch.delenv("TOGETHER_DISABLE_VERSION_CHECK", raising=False)
    monkeypatch.setattr(_version_check, "__version__", "1.0.0")
    monkeypatch.setattr(_version_check, "_latest_version", lambda: "1.1.0")
    monkeypatch.setattr(_version_check, "_upgrade_command", lambda: ["upgrade"])
    monkeypatch.setattr(_version_check, "error_console", output)
    monkeypatch.setattr(_version_check, "confirm", confirm)
    monkeypatch.setattr(_version_check.subprocess, "run", run)

    version_check = _version_check.VersionCheck()
    await version_check.inform(non_interactive=False, allow_prompt=True)

    confirm.assert_awaited_once_with("Upgrade the Together CLI now?")
    run.assert_called_once_with(["upgrade"], check=False)
    assert "upgraded" in output.print.call_args.args[0]


async def test_version_check_prompt_interrupt_does_not_escape(monkeypatch: pytest.MonkeyPatch) -> None:
    confirm = AsyncMock(side_effect=KeyboardInterrupt)
    monkeypatch.delenv("TOGETHER_DISABLE_VERSION_CHECK", raising=False)
    monkeypatch.setattr(_version_check, "__version__", "1.0.0")
    monkeypatch.setattr(_version_check, "_latest_version", lambda: "1.1.0")
    monkeypatch.setattr(_version_check, "confirm", confirm)

    version_check = _version_check.VersionCheck()
    await version_check.inform(non_interactive=False, allow_prompt=True)

    confirm.assert_awaited_once()


async def test_version_check_fails_open(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail() -> str:
        raise TimeoutError

    monkeypatch.delenv("TOGETHER_DISABLE_VERSION_CHECK", raising=False)
    monkeypatch.setattr(_version_check, "_latest_version", fail)

    version_check = _version_check.VersionCheck()
    await version_check.inform(non_interactive=False, allow_prompt=True)
