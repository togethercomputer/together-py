from __future__ import annotations

import os
import json

import httpx
import pytest
from respx import MockRouter

from tests.cli.utils import CliRunner

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


class TestAgentJsonDefault:
    @pytest.mark.respx(base_url=base_url)
    def test_agent_defaults_to_json(self, respx_mock: MockRouter, capsys: pytest.CaptureFixture[str]) -> None:
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))
        result = CliRunner(capsys, agent=True).invoke(["whoami"])

        assert result.exit_code == 0, result.output
        payload = json.loads(result.out_out)
        assert payload["project_id"] == "proj"
        assert payload["organization_name"] == "Acme Org"
        assert payload["project_name"] == "My Project"

    @pytest.mark.respx(base_url=base_url)
    def test_agent_no_json_stays_text(self, respx_mock: MockRouter, capsys: pytest.CaptureFixture[str]) -> None:
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))
        result = CliRunner(capsys, agent=True).invoke(["whoami", "--no-json"])

        assert result.exit_code == 0, result.output
        assert "My Project" in result.output
        assert "proj" in result.output
        with pytest.raises(json.JSONDecodeError):
            json.loads(result.out_out)

    @pytest.mark.respx(base_url=base_url)
    def test_human_stays_text_without_flag(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))
        result = cli_runner.invoke(["whoami"])

        assert result.exit_code == 0, result.output
        assert "My Project" in result.output
        with pytest.raises(json.JSONDecodeError):
            json.loads(result.out_out)

    def test_agent_validation_error_is_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = CliRunner(capsys, agent=True).invoke(["endpoints", "update", "endpoint-123"])

        assert result.exit_code == 1
        payload = json.loads(result.out_out)
        assert payload["error"] == "At least one update option must be specified"

    def test_agent_usage_error_is_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = CliRunner(capsys, agent=True).invoke(["not-a-command"])

        assert result.exit_code == 1
        payload = json.loads(result.out_out)
        assert "error" in payload
        assert payload["error"]

    def test_agent_missing_api_key_is_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        runner = CliRunner(capsys, agent=True)
        runner.env.pop("TOGETHER_API_KEY", None)
        result = runner.invoke(["whoami"])

        assert result.exit_code == 1
        payload = json.loads(result.out_out)
        assert "API key" in payload["error"]
        assert "TOGETHER_API_KEY" in payload["error"]

    def test_human_validation_error_stays_text(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["endpoints", "update", "endpoint-123"])

        assert result.exit_code == 1
        assert "At least one update option must be specified" in result.output
        with pytest.raises(json.JSONDecodeError):
            json.loads(result.out_out)
