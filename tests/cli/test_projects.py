from __future__ import annotations

import os
import json
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from tests.cli.utils import CliRunner

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


def _project_body(
    project_id: str = "proj",
    name: str = "My Project",
    **overrides: Any,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": project_id,
        "name": name,
        "organization_id": "org-1",
        "organization_name": "Acme Org",
        "slug": "mine",
    }
    body.update(overrides)
    return body


class TestProjectsList:
    @pytest.mark.respx(base_url=base_url)
    def test_list_sends_cursor_pagination(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.get("/v1/projects").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_project_body()], "next_cursor": "next"},
            )
        )

        result = cli_runner.invoke(["projects", "list", "--limit", "10", "--after", "tok", "--json"])

        assert result.exit_code == 0, result.output
        url = str(cast(Call, route.calls[0]).request.url)
        assert "limit=10" in url
        assert "after=tok" in url
        payload = json.loads(result.output)
        assert payload["next_cursor"] == "next"
        assert payload["data"][0]["id"] == "proj"

    @pytest.mark.respx(base_url=base_url)
    @pytest.mark.parametrize("command", ["list", "ls"])
    def test_list_table_marks_current_project(
        self, command: str, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/v1/projects").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [
                        _project_body(),
                        _project_body(project_id="proj-2", name="Other", slug="other-proj"),
                    ],
                    "next_cursor": "page-2",
                },
            )
        )

        result = cli_runner.invoke(["projects", command])

        assert result.exit_code == 0, result.output
        assert "My Project" in result.output
        assert "(current)" in result.output
        assert "Other" in result.output
        assert "mine" in result.output
        assert "Acme Org" in result.output
        assert "org-1" in result.output
        assert "tg projects list --after page-2" in result.output
        assert "tg switch" not in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_list_hints_switch_when_no_project_selected(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/v3/whoami").mock(
            return_value=httpx.Response(
                200,
                json={
                    "type": "user_jwt",
                    "user": {"id": "user-1"},
                },
            )
        )
        respx_mock.get("/v1/projects").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_project_body()], "next_cursor": None},
            )
        )
        del cli_runner.env["TOGETHER_PROJECT_ID"]

        result = cli_runner.invoke(["projects", "list"])

        assert result.exit_code == 0, result.output
        assert "(current)" not in result.output
        assert "tg switch <project-id>" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_list_empty(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/v1/projects").mock(
            return_value=httpx.Response(200, json={"object": "list", "data": [], "next_cursor": None})
        )

        result = cli_runner.invoke(["projects", "list"])

        assert result.exit_code == 0, result.output
        assert "No projects found." in result.output
