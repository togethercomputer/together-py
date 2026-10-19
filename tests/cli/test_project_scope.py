from __future__ import annotations

import os
import json
from pathlib import Path

import httpx
import pytest
from respx import MockRouter

from tests.cli.utils import CliRunner
from together.lib.cli.auth import TogetherAuth, StoredCredentials, save_stored_credentials
from together.types.project import Project
from together.lib.cli.utils._project_scope import ProjectScopeSwitched, explain_project_scope, offer_project_after_login

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")

_FORBIDDEN = {"error": {"message": "permission denied", "type": "permission_error"}}


def _flat(output: str) -> str:
    return " ".join(output.split())


def _login(cli_runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, project_id: str | None) -> None:
    creds = tmp_path / "credentials.json"
    monkeypatch.setenv("TOGETHER_CREDENTIALS_PATH", str(creds))
    save_stored_credentials(StoredCredentials(access_token="stored-jwt", issuer=base_url, project_id=project_id))
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds)


class TestProjectScope:
    @pytest.mark.respx(base_url=base_url)
    def test_unscoped_login_tells_you_to_switch(
        self, respx_mock: MockRouter, cli_runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _login(cli_runner, tmp_path, monkeypatch, project_id=None)
        respx_mock.get("/v2/projects/proj/models").mock(return_value=httpx.Response(403, json=_FORBIDDEN))

        result = cli_runner.invoke(["models", "list"])

        assert result.exit_code == 1, result.output
        assert "tg switch proj" in _flat(result.output)
        assert "permission denied" not in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_unscoped_login_401_prompts_for_a_project(
        self, respx_mock: MockRouter, cli_runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _login(cli_runner, tmp_path, monkeypatch, project_id=None)
        respx_mock.get("/v2/projects/proj/models").mock(
            return_value=httpx.Response(
                401, json={"error": {"message": "unauthorized", "type": "authentication_error"}}
            )
        )

        result = cli_runner.invoke(["models", "list"])

        assert result.exit_code == 1, result.output
        assert "tg switch proj" in _flat(result.output)
        assert "tg login" not in result.output
        assert "unauthorized" not in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_unscoped_login_401_after_rejected_refresh_says_login(
        self, respx_mock: MockRouter, cli_runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        creds = tmp_path / "credentials.json"
        monkeypatch.setenv("TOGETHER_CREDENTIALS_PATH", str(creds))
        save_stored_credentials(
            StoredCredentials(access_token="stored-jwt", refresh_token="rt", issuer=base_url, project_id=None)
        )
        cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds)
        monkeypatch.setattr("together.lib.cli._session_is_interactive", lambda: True)
        respx_mock.get(f"{base_url}/.well-known/openid-configuration").mock(
            return_value=httpx.Response(
                200,
                json={
                    "issuer": base_url,
                    "authorization_endpoint": f"{base_url}/oauth/authorize",
                    "token_endpoint": f"{base_url}/oauth/token",
                },
            )
        )
        respx_mock.post(f"{base_url}/oauth/token").mock(
            return_value=httpx.Response(401, json={"error": "invalid_grant"})
        )
        respx_mock.get("/v2/projects/proj/models").mock(
            return_value=httpx.Response(
                401, json={"error": {"message": "unauthorized", "type": "authentication_error"}}
            )
        )

        result = cli_runner.invoke(["models", "list"])

        assert result.exit_code == 1, result.output
        assert "tg login" in result.output
        assert "select a project scope" not in result.output.lower()
        assert "tg switch" not in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_project_token_401_is_not_a_scope_prompt(
        self, respx_mock: MockRouter, cli_runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _login(cli_runner, tmp_path, monkeypatch, project_id="proj")
        respx_mock.get(f"{base_url}/.well-known/openid-configuration").mock(
            return_value=httpx.Response(
                200,
                json={
                    "issuer": base_url,
                    "authorization_endpoint": f"{base_url}/oauth/authorize",
                    "token_endpoint": f"{base_url}/oauth/token",
                },
            )
        )
        respx_mock.post(f"{base_url}/oauth/token").mock(
            return_value=httpx.Response(401, json={"error": "invalid_grant"})
        )
        respx_mock.get("/v2/projects/proj/models").mock(
            return_value=httpx.Response(
                401, json={"error": {"message": "unauthorized", "type": "authentication_error"}}
            )
        )

        result = cli_runner.invoke(["models", "list"])

        assert result.exit_code == 1, result.output
        assert "unauthorized" in result.output
        assert "select a project scope" not in result.output.lower()
        assert "tg login" not in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_unscoped_login_400_stays_an_api_error(
        self, respx_mock: MockRouter, cli_runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _login(cli_runner, tmp_path, monkeypatch, project_id=None)
        respx_mock.get("/v2/projects/proj/models").mock(
            return_value=httpx.Response(400, json={"error": {"message": "bad model", "type": "invalid_request_error"}})
        )

        result = cli_runner.invoke(["models", "list"])

        assert result.exit_code == 1, result.output
        assert "bad model" in result.output
        assert "tg switch" not in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_unscoped_login_json(
        self, respx_mock: MockRouter, cli_runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _login(cli_runner, tmp_path, monkeypatch, project_id=None)
        respx_mock.get("/v2/projects/proj/models").mock(return_value=httpx.Response(403, json=_FORBIDDEN))

        result = cli_runner.invoke(["models", "list", "--json"])

        assert result.exit_code == 1, result.output
        assert "tg switch proj" in json.loads(result.output)["error"]

    def test_missing_project_tells_you_to_list_then_switch(
        self, cli_runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _login(cli_runner, tmp_path, monkeypatch, project_id=None)
        del cli_runner.env["TOGETHER_PROJECT_ID"]

        result = cli_runner.invoke(["models", "list"])

        assert result.exit_code == 1, result.output
        text = _flat(result.output)
        assert "tg projects list" in text
        assert "tg switch <project-id>" in text

    @pytest.mark.respx(base_url=base_url)
    def test_other_project_tells_you_to_switch_to_it(
        self, respx_mock: MockRouter, cli_runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _login(cli_runner, tmp_path, monkeypatch, project_id="proj_a")
        respx_mock.get("/v2/projects/proj_b/models").mock(return_value=httpx.Response(403, json=_FORBIDDEN))

        result = cli_runner.invoke(["--project", "proj_b", "models", "list"])

        assert result.exit_code == 1, result.output
        text = _flat(result.output)
        assert "scoped to project proj_a, not proj_b" in text
        assert "tg switch proj_b" in text

    @pytest.mark.respx(base_url=base_url)
    def test_matching_scope_keeps_the_api_error(
        self, respx_mock: MockRouter, cli_runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _login(cli_runner, tmp_path, monkeypatch, project_id="proj")
        respx_mock.get("/v2/projects/proj/models").mock(return_value=httpx.Response(403, json=_FORBIDDEN))

        result = cli_runner.invoke(["models", "list"])

        assert result.exit_code == 1, result.output
        assert "permission denied" in result.output
        assert "tg switch" not in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_api_key_without_a_project_is_unchanged(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/v3/whoami").mock(
            return_value=httpx.Response(200, json={"type": "user_jwt", "user": {"id": "user-1"}})
        )
        del cli_runner.env["TOGETHER_PROJECT_ID"]

        result = cli_runner.invoke(["models", "list"])

        assert result.exit_code == 1, result.output
        assert "Missing project_id" in result.output
        assert "tg switch" not in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_whoami_forbidden_is_not_a_switch_hint(
        self, respx_mock: MockRouter, cli_runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _login(cli_runner, tmp_path, monkeypatch, project_id=None)
        respx_mock.get(f"{base_url}/v3/whoami").mock(return_value=httpx.Response(403, json=_FORBIDDEN))

        result = cli_runner.invoke(["whoami"])

        assert result.exit_code == 1, result.output
        assert "tg switch" not in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_interactive_rejection_reruns_after_switch(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _login(cli_runner, tmp_path, monkeypatch, project_id=None)
        monkeypatch.setattr("together.lib.cli._session_is_interactive", lambda: True)

        headers: list[str | None] = []

        def models(request: httpx.Request) -> httpx.Response:
            headers.append(request.headers.get("authorization"))
            if len(headers) == 1:
                return httpx.Response(403, json=_FORBIDDEN)
            return httpx.Response(200, json={"object": "list", "data": [], "next_cursor": None})

        respx_mock.get("/v2/projects/proj/models").mock(side_effect=models)
        respx_mock.get("/v1/projects").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [_project_row()],
                    "next_cursor": None,
                },
            )
        )

        async def select(_projects: list[Project], *, preferred: str | None, message: str) -> str:
            assert message == "Select a project scope"
            assert preferred == "proj"
            return "proj"

        def switch(_self: TogetherAuth, project_id: str) -> StoredCredentials:
            assert project_id == "proj"
            return StoredCredentials(access_token="project-jwt", project_id=project_id)

        monkeypatch.setattr("together.lib.cli.utils._project_scope.select_project", select)
        monkeypatch.setattr(TogetherAuth, "switch", switch)

        result = cli_runner.invoke(["models", "list"])

        assert result.exit_code == 0, result.output
        assert "You must select a project scope to work in." in result.output
        assert "Switched to project" in result.output
        assert headers == ["Bearer stored-jwt", "Bearer project-jwt"]


def _project_row() -> dict[str, str]:
    return {
        "id": "proj",
        "name": "My Project",
        "organization_id": "org-1",
        "organization_name": "Acme",
        "slug": "mine",
    }


def _project(project_id: str) -> Project:
    return Project(id=project_id, name=project_id, organization_id="org", organization_name="Org", slug=project_id)


class _Projects:
    def __init__(self, projects: list[Project]) -> None:
        self._projects = projects

    async def list(self, **_kwargs: object) -> object:
        return type("Page", (), {"data": self._projects})()


class _Client:
    def __init__(self, projects: list[Project]) -> None:
        self.projects = _Projects(projects)


async def test_offer_project_after_login_switches_only_project(monkeypatch: pytest.MonkeyPatch) -> None:
    switched: list[str] = []
    prompted: list[list[str]] = []

    async def select(projects: list[Project], *, preferred: str | None) -> str:
        prompted.append([project.id for project in projects])
        assert preferred is None
        return projects[0].id

    def switch(_self: TogetherAuth, project_id: str) -> StoredCredentials:
        switched.append(project_id)
        return StoredCredentials(access_token="project-jwt", project_id=project_id)

    monkeypatch.setattr("together.lib.cli.utils._project_scope.select_project", select)
    monkeypatch.setattr(TogetherAuth, "switch", switch)

    client = _Client([_project("proj_a")])
    assert await offer_project_after_login(client, interactive=True) == "proj_a"
    assert await offer_project_after_login(client, interactive=False) == "proj_a"
    assert switched == ["proj_a", "proj_a"]
    assert prompted == []


async def test_offer_project_after_login_prompts_when_several(monkeypatch: pytest.MonkeyPatch) -> None:
    switched: list[str] = []

    async def select(projects: list[Project], *, preferred: str | None) -> str:
        assert [project.id for project in projects] == ["proj_a", "proj_b"]
        assert preferred is None
        return "proj_b"

    def switch(_self: TogetherAuth, project_id: str) -> StoredCredentials:
        switched.append(project_id)
        return StoredCredentials(access_token="project-jwt", project_id=project_id)

    monkeypatch.setattr("together.lib.cli.utils._project_scope.select_project", select)
    monkeypatch.setattr(TogetherAuth, "switch", switch)

    client = _Client([_project("proj_a"), _project("proj_b")])
    assert await offer_project_after_login(client, interactive=True) == "proj_b"
    assert switched == ["proj_b"]
    assert await offer_project_after_login(client, interactive=False) is None
    assert switched == ["proj_b"]


async def test_prompt_switches_and_stops(monkeypatch: pytest.MonkeyPatch) -> None:
    switched: list[str] = []

    async def confirm(_message: str) -> bool:
        return True

    def switch(_self: TogetherAuth, project_id: str) -> StoredCredentials:
        switched.append(project_id)
        return StoredCredentials(access_token="project-jwt", project_id=project_id)

    monkeypatch.setattr("together.lib.cli.utils._project_scope.confirm", confirm)
    monkeypatch.setattr(TogetherAuth, "switch", switch)

    with pytest.raises(ProjectScopeSwitched) as exc:
        await explain_project_scope(
            PermissionDenied(),
            command="models list",
            using_stored_token=True,
            token_project=None,
            client_project="proj_b",
            non_interactive=False,
        )

    assert exc.value.project_id == "proj_b"
    assert exc.value.access_token == "project-jwt"
    assert switched == ["proj_b"]


async def test_prompt_lists_projects_to_switch_to(monkeypatch: pytest.MonkeyPatch) -> None:
    switched: list[str] = []
    offered: list[tuple[list[str], str | None]] = []

    async def select(projects: list[Project], *, preferred: str | None, message: str) -> str:
        offered.append(([project.id for project in projects], preferred))
        assert message == "Select a project scope"
        return "proj_a"

    class _Page:
        data = [
            Project(id="proj_a", name="Alpha", organization_id="org", organization_name="Org", slug="alpha"),
            Project(id="proj_b", name="Beta", organization_id="org", organization_name="Org", slug="beta"),
        ]

    class _Projects:
        async def list(self, **kwargs: object) -> _Page:
            assert kwargs["limit"] == 100
            return _Page()

    class _Client:
        projects = _Projects()

    def switch(_self: TogetherAuth, project_id: str) -> StoredCredentials:
        switched.append(project_id)
        return StoredCredentials(access_token="project-jwt", project_id=project_id)

    monkeypatch.setattr("together.lib.cli.utils._project_scope.select_project", select)
    monkeypatch.setattr(TogetherAuth, "switch", switch)

    with pytest.raises(ProjectScopeSwitched) as exc:
        await explain_project_scope(
            PermissionDenied(),
            command="models list",
            using_stored_token=True,
            token_project=None,
            client_project="proj_b",
            non_interactive=False,
            client=_Client(),
        )

    assert exc.value.project_id == "proj_a"
    assert offered == [(["proj_a", "proj_b"], "proj_b")]
    assert switched == ["proj_a"]


def PermissionDenied() -> Exception:
    from together import PermissionDeniedError

    request = httpx.Request("GET", "https://api.together.ai/v2/projects/proj_b/models")
    response = httpx.Response(403, json=_FORBIDDEN, request=request)
    return PermissionDeniedError("permission denied", response=response, body=_FORBIDDEN)
