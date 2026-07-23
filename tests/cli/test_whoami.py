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


class TestWhoami:
    @pytest.mark.respx(base_url=base_url)
    def test_whoami_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))

        result = cli_runner.invoke(["whoami", "--json"])

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["project_id"] == "proj"
        assert payload["organization_id"] == "org-1"
        assert payload["project_slug"] == "my-project"

    @pytest.mark.respx(base_url=base_url)
    def test_whoami_human(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))

        result = cli_runner.invoke(["whoami"])

        assert result.exit_code == 0, result.output
        assert "My Project" in result.output
        assert "proj" in result.output
        assert "Acme Org" in result.output
        assert "org-1" in result.output
