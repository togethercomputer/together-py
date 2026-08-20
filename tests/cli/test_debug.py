from __future__ import annotations

import os
import json
import logging

import httpx
import pytest
from respx import MockRouter

from together import APIError
from tests.cli.utils import API_KEY, CliRunner
from together._version import __version__

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


def _whoami_body() -> dict[str, str]:
    return {
        "api_key_id": "key-1",
        "organization_id": "org-1",
        "organization_name": "Acme Org",
        "project_id": "proj",
        "project_name": "My Project",
        "project_slug": "my-project",
        "user_id": "user-1",
    }


class TestCliDebug:
    def test_help_lists_debug_flag(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["--help"])
        assert result.exit_code == 0
        assert "--debug" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_debug_whoami_is_structured_and_redacted(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/whoami").mock(
            return_value=httpx.Response(
                200,
                json=_whoami_body(),
                headers={"x-request-id": "req_test_123", "server": "cloudflare"},
            )
        )

        result = cli_runner.invoke(["whoami", "--debug"])

        assert result.exit_code == 0, result.output
        assert "My Project" in result.out_out
        err = result.err_out
        assert "debug" in err
        assert __version__ in err
        assert "tg whoami" in err
        assert "GET" in err
        assert "200" in err
        assert "req_test_123" in err
        assert "project_id" in err
        assert API_KEY not in err
        assert "Request options:" not in err
        assert "Sending HTTP Request:" not in err
        assert "HTTP Response:" not in err
        assert "Headers(" not in err
        assert "Analytics event sending" not in err
        assert "server: cloudflare" not in err.lower()

    @pytest.mark.respx(base_url=base_url)
    def test_debug_keeps_json_stdout_clean(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))

        result = cli_runner.invoke(["whoami", "--json", "--debug"])

        assert result.exit_code == 0, result.output
        payload = json.loads(result.out_out)
        assert payload["project_id"] == "proj"
        assert "GET" in result.err_out
        assert "debug" in result.err_out

    @pytest.mark.respx(base_url=base_url)
    def test_debug_shows_error_response_body(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/whoami").mock(
            return_value=httpx.Response(
                401,
                json={"error": {"message": "Invalid API key", "type": "invalid_request_error"}},
                headers={"x-request-id": "req_err_1"},
            )
        )

        with pytest.raises(APIError):
            cli_runner.invoke(["whoami", "--debug"])
        captured = cli_runner.capsys.readouterr()
        err = captured.err
        assert "401" in err
        assert "req_err_1" in err
        assert "Invalid API key" in err
        assert API_KEY not in err
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))

        result = cli_runner.invoke(["whoami"])

        assert result.exit_code == 0, result.output
        assert "→" not in result.err_out
        assert "tg whoami" not in result.err_out

    @pytest.mark.respx(base_url=base_url)
    def test_debug_does_not_leave_logger_hooked(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))

        first = cli_runner.invoke(["whoami", "--debug"])
        assert first.exit_code == 0, first.output

        together_logger = logging.getLogger("together")
        from together.lib.cli.utils._debug import CliDebugLogHandler, is_enabled

        assert is_enabled() is False
        assert not any(isinstance(handler, CliDebugLogHandler) for handler in together_logger.handlers)

        second = cli_runner.invoke(["whoami"])
        assert second.exit_code == 0, second.output
        assert "→" not in second.err_out
