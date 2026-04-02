from __future__ import annotations

import os

from click.testing import CliRunner

from together.lib.cli import main
from together._version import __version__

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
API_KEY = "0000000000000000000000000000000000000000"


class TestMainGlobalOptions:
    def test_version_exits_zero(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_help_without_api_key_still_works(self) -> None:
        runner = CliRunner(env={"TOGETHER_BASE_URL": base_url})
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "together" in result.output.lower() or "CLI" in result.output

    def test_timeout_and_max_retries_passed_to_client(self) -> None:
        from unittest.mock import patch

        with patch("together.lib.cli.together.Together") as ctor:
            runner = CliRunner(
                env={"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY},
            )
            r = runner.invoke(
                main,
                [
                    "--timeout",
                    "99",
                    "--max-retries",
                    "3",
                    "models",
                    "--help",
                ],
            )
            assert r.exit_code == 0
            call_kw = ctor.call_args.kwargs
            assert call_kw.get("timeout") == 99
            assert call_kw.get("max_retries") == 3
