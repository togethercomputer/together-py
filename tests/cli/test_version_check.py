from __future__ import annotations

import json
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


async def test_check_for_update_prints_upgrade_command_when_non_interactive(monkeypatch: pytest.MonkeyPatch) -> None:
    output = MagicMock()
    monkeypatch.delenv("TOGETHER_DISABLE_VERSION_CHECK", raising=False)
    monkeypatch.setattr(_version_check, "__version__", "1.0.0")
    monkeypatch.setattr(_version_check, "_latest_version", lambda: "1.1.0")
    monkeypatch.setattr(
        _version_check, "_upgrade_command", lambda: ["python", "-m", "pip", "install", "-U", "together"]
    )
    monkeypatch.setattr(_version_check, "error_console", output)

    await _version_check.check_for_update(non_interactive=True)

    rendered = " ".join(call.args[0] for call in output.print.call_args_list)
    assert "1.0.0 → 1.1.0" in rendered
    assert "python -m pip install -U together" in rendered


async def test_check_for_update_prompts_and_upgrades_on_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    output = MagicMock()
    confirm = AsyncMock(return_value=True)
    run = MagicMock(return_value=subprocess.CompletedProcess(["upgrade"], returncode=0))
    monkeypatch.delenv("TOGETHER_DISABLE_VERSION_CHECK", raising=False)
    monkeypatch.setattr(_version_check, "__version__", "1.0.0")
    monkeypatch.setattr(_version_check, "_latest_version", lambda: "1.1.0")
    monkeypatch.setattr(_version_check, "_upgrade_command", lambda: ["upgrade"])
    monkeypatch.setattr(_version_check, "_is_interactive", lambda: True)
    monkeypatch.setattr(_version_check, "error_console", output)
    monkeypatch.setattr(_version_check, "confirm", confirm)
    monkeypatch.setattr(_version_check.subprocess, "run", run)

    await _version_check.check_for_update(non_interactive=False)

    confirm.assert_awaited_once_with("Upgrade the Together CLI now?")
    run.assert_called_once_with(["upgrade"], check=False)
    assert "upgraded" in output.print.call_args.args[0]


async def test_check_for_update_fails_open(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail() -> str:
        raise TimeoutError

    monkeypatch.delenv("TOGETHER_DISABLE_VERSION_CHECK", raising=False)
    monkeypatch.setattr(_version_check, "_latest_version", fail)

    await _version_check.check_for_update(non_interactive=False)
