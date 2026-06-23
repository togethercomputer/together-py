from __future__ import annotations

import os
import json

import httpx
import pytest
from respx import MockRouter

from tests.cli.utils import CliRunner
from together._version import __version__

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
API_KEY = "0000000000000000000000000000000000000000"

WHOAMI_RESPONSE = {
    "api_key_id": "key-123",
    "organization_id": "org-123",
    "organization_name": "Acme Org",
    "project_id": "proj-123",
    "project_name": "Inference Project",
    "project_slug": "inference-project",
}


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


class TestWhoami:
    @pytest.mark.respx(base_url=base_url)
    def test_whoami(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=WHOAMI_RESPONSE))

        result = cli_runner.invoke(["whoami"])

        assert result.exit_code == 0
        assert route.called
        assert "Api Key Id:" in result.output
        assert "key-123" in result.output
        assert "Organization Name:" in result.output
        assert "Acme Org" in result.output
        assert "Project Slug:" in result.output
        assert "inference-project" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_whoami_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=WHOAMI_RESPONSE))

        result = cli_runner.invoke(["whoami", "--json"])

        assert result.exit_code == 0
        assert json.loads(result.out_out.lstrip("\n")) == WHOAMI_RESPONSE
