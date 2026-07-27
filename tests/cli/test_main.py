from __future__ import annotations

import os
import json
from pathlib import Path

import pytest

from tests.cli.utils import CliRunner
from together._version import __version__

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
API_KEY = "0000000000000000000000000000000000000000"


class TestMainGlobalOptions:
    def test_version_exits_zero(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["--version"])
        assert result.exit_code == 0
        assert __version__ in result.out_out

    def test_help_without_api_key_still_works(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["--help"])
        assert result.exit_code == 0
        assert "together" in result.output.lower() or "CLI" in result.output

    def test_timeout_and_max_retries_passed_to_client(self, cli_runner: CliRunner) -> None:
        from unittest.mock import AsyncMock, patch

        # Subcommand --help is handled before the meta default runs, so `AsyncTogether` is never
        # constructed for `models --help`. Bare `models` still runs the launcher (usage + exit 0).
        with patch("together.lib.cli.AsyncTogether") as ctor:
            ctor.return_value = AsyncMock()
            r = cli_runner.invoke(
                [
                    "--timeout",
                    "99",
                    "--max-retries",
                    "3",
                    "models",
                ],
            )
            assert r.exit_code == 0
            assert ctor.called
            call_kw = ctor.call_args.kwargs
            assert call_kw.get("timeout") == 99
            assert call_kw.get("max_retries") == 3

    def test_version_check_runs_after_command_with_non_interactive_option(
        self, monkeypatch: pytest.MonkeyPatch, cli_runner: CliRunner
    ) -> None:
        calls: list[tuple[bool, bool, str]] = []

        class FakeVersionCheck:
            async def inform(self, *, non_interactive: bool, allow_prompt: bool) -> None:
                calls.append((non_interactive, allow_prompt, cli_runner.capsys.readouterr().out))

        monkeypatch.setattr("together.lib.cli.VersionCheck", FakeVersionCheck)

        result = cli_runner.invoke(["--non-interactive", "telemetry", "status"])

        assert result.exit_code == 0
        assert len(calls) == 1
        assert calls[0][0] is True
        assert calls[0][1] is True
        assert "Telemetry:" in calls[0][2]

    def test_version_check_does_not_prompt_after_command_failure(
        self, monkeypatch: pytest.MonkeyPatch, cli_runner: CliRunner
    ) -> None:
        calls: list[tuple[bool, bool]] = []

        class FakeVersionCheck:
            async def inform(self, *, non_interactive: bool, allow_prompt: bool) -> None:
                calls.append((non_interactive, allow_prompt))

        monkeypatch.setattr("together.lib.cli.VersionCheck", FakeVersionCheck)

        result = cli_runner.invoke(["unknown-command"])

        assert result.exit_code == 1
        assert calls == [(True, False)]

    def test_update_notice_does_not_corrupt_json_output(
        self, monkeypatch: pytest.MonkeyPatch, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        cli_runner.env.pop("TOGETHER_DISABLE_VERSION_CHECK")
        monkeypatch.setattr("together.lib.cli.utils._version_check.__version__", "1.0.0")
        monkeypatch.setattr("together.lib.cli.utils._version_check._latest_version", lambda: "1.1.0")
        monkeypatch.setattr(
            "together.lib.cli.utils._version_check._upgrade_command",
            lambda: ["python", "-m", "pip", "install", "--upgrade", "together"],
        )
        monkeypatch.setattr(
            "together.lib.cli.utils._version_check._cache_path",
            lambda: tmp_path / "version-check.json",
        )

        result = cli_runner.invoke(["--json", "telemetry", "status"])

        assert result.exit_code == 0
        assert json.loads(result.out_out)["telemetry"] in {"enabled", "disabled"}
        assert "1.0.0 → 1.1.0" not in result.out_out
        assert "1.0.0 → 1.1.0" in result.err_out
