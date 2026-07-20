from __future__ import annotations

import os

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

    def test_non_interactive_option_is_forwarded_to_version_check(
        self, monkeypatch: pytest.MonkeyPatch, cli_runner: CliRunner
    ) -> None:
        from unittest.mock import AsyncMock

        check_for_update = AsyncMock()
        monkeypatch.setattr("together.lib.cli.check_for_update", check_for_update)

        result = cli_runner.invoke(["--non-interactive", "models"])

        assert result.exit_code == 0
        check_for_update.assert_awaited_once_with(non_interactive=True)
