from __future__ import annotations

import os
import json
from typing import cast

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from tests.cli.utils import CliRunner

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


PROJECT_LIST_BODY = {
    "object": "list",
    "data": [
        {
            "id": "proj_1",
            "name": "My Project",
            "slug": "slug",
            "organization_id": "org_1",
            "organization_name": "Acme",
        }
    ],
    "next_cursor": "proj_next",
}


class TestProjectsList:
    @pytest.mark.respx(base_url=base_url)
    def test_list_projects_json_sends_pagination(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.get("/projects").mock(return_value=httpx.Response(200, json=PROJECT_LIST_BODY))

        result = cli_runner.invoke(["projects", "list", "--limit", "5", "--after", "tok", "--json"])

        assert result.exit_code == 0, result.output
        url = str(cast(Call, route.calls[0]).request.url)
        assert "limit=5" in url
        assert "after=tok" in url
        payload = json.loads(result.output)
        assert payload["data"][0]["id"] == "proj_1"
        assert payload["next_cursor"] == "proj_next"

    @pytest.mark.respx(base_url=base_url)
    def test_list_projects_table(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/projects").mock(
            return_value=httpx.Response(200, json={**PROJECT_LIST_BODY, "next_cursor": None})
        )

        result = cli_runner.invoke(["projects", "ls"])

        assert result.exit_code == 0, result.output
        assert "proj_1" in result.output
        assert "My Project" in result.output
        assert "slug" in result.output
        assert "Acme" in result.output
