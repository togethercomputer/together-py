from __future__ import annotations

import os
import json
from pathlib import Path

import httpx
import pytest
from respx import MockRouter

from tests.cli.utils import CliRunner

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


def _whoami_body() -> dict[str, object]:
    return {
        "type": "project_api_key",
        "api_key": {"id": "key-1"},
        "organization": {"id": "org-1", "name": "Acme Org"},
        "project": {"id": "proj", "name": "My Project", "slug": "my-project"},
    }


class TestWhoami:
    @pytest.mark.respx(base_url=base_url)
    def test_whoami_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/v3/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))

        result = cli_runner.invoke(["whoami", "--json"])

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["type"] == "project_api_key"
        assert payload["project"]["id"] == "proj"
        assert payload["organization"]["id"] == "org-1"
        assert payload["project"]["slug"] == "my-project"

    @pytest.mark.respx(base_url=base_url)
    def test_whoami_human(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/v3/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))

        result = cli_runner.invoke(["whoami"])

        assert result.exit_code == 0, result.output
        assert "My Project" in result.output
        assert "proj" in result.output
        assert "Acme Org" in result.output
        assert "org-1" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_whoami_prefers_stored_access_token_over_env_api_key(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from together.lib.cli.auth import StoredCredentials, save_stored_credentials

        creds = tmp_path / "credentials.json"
        monkeypatch.setenv("TOGETHER_CREDENTIALS_PATH", str(creds))
        save_stored_credentials(StoredCredentials(access_token="stored-jwt", issuer=base_url))
        cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds)
        cli_runner.env["TOGETHER_API_KEY"] = "env-key-should-not-be-used"

        seen: list[str | None] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request.headers.get("authorization"))
            return httpx.Response(200, json=_whoami_body())

        respx_mock.get("/v3/whoami").mock(side_effect=handler)

        result = cli_runner.invoke(["whoami", "--json"])
        assert result.exit_code == 0, result.output
        assert seen == ["Bearer stored-jwt"]

    @pytest.mark.respx(base_url=base_url)
    def test_whoami_explicit_api_key_wins_over_stored_token(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from together.lib.cli.auth import StoredCredentials, save_stored_credentials

        creds = tmp_path / "credentials.json"
        monkeypatch.setenv("TOGETHER_CREDENTIALS_PATH", str(creds))
        save_stored_credentials(StoredCredentials(access_token="stored-jwt"))
        cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds)
        cli_runner.env["TOGETHER_API_KEY"] = "env-key-should-not-be-used"

        seen: list[str | None] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request.headers.get("authorization"))
            return httpx.Response(200, json=_whoami_body())

        respx_mock.get("/v3/whoami").mock(side_effect=handler)

        result = cli_runner.invoke(["--api-key", "flag-key", "whoami", "--json"])
        assert result.exit_code == 0, result.output
        assert seen == ["Bearer flag-key"]

    @pytest.mark.respx(base_url=base_url)
    def test_debug_logs_redacted_authorization(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from together.lib.cli.auth import StoredCredentials, save_stored_credentials

        jwt = "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ1c2VyLTEiLCJlbWFpbCI6ImEifQ.signaturetailhere"
        creds = tmp_path / "credentials.json"
        monkeypatch.setenv("TOGETHER_CREDENTIALS_PATH", str(creds))
        save_stored_credentials(StoredCredentials(access_token=jwt, issuer=base_url))
        cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds)
        cli_runner.env.pop("TOGETHER_API_KEY", None)

        respx_mock.get("/v3/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))

        result = cli_runner.invoke(["--debug", "whoami", "--json"])
        assert result.exit_code == 0, result.output
        # `--debug` shows only the last four characters of the stored `tg login` token.
        assert "…here" in result.err_out
        assert jwt not in result.output
        assert "eyJzdWIi" not in result.output
        assert "signaturetailh" not in result.output


@pytest.mark.respx(base_url=base_url)
def test_whoami_refreshes_expired_stored_token_before_calling(
    respx_mock: MockRouter,
    cli_runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from together.lib.cli.auth import TogetherAuth, StoredCredentials, save_stored_credentials

    creds = tmp_path / "credentials.json"
    monkeypatch.setenv("TOGETHER_CREDENTIALS_PATH", str(creds))
    save_stored_credentials(
        StoredCredentials(access_token="expired-jwt", refresh_token="rt", expires_at=1, issuer=base_url)
    )
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds)

    def fake_refresh(_self: TogetherAuth, *, force: bool = False, name: str | None = None) -> StoredCredentials:
        assert force is False and name is None
        updated = StoredCredentials(access_token="fresh-jwt", refresh_token="rt", issuer=base_url)
        save_stored_credentials(updated)
        return updated

    monkeypatch.setattr(TogetherAuth, "refresh", fake_refresh)
    seen: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.headers.get("authorization"))
        return httpx.Response(200, json=_whoami_body())

    respx_mock.get("/v3/whoami").mock(side_effect=handler)
    result = cli_runner.invoke(["whoami", "--json"])
    assert result.exit_code == 0, result.output
    assert seen == ["Bearer fresh-jwt"]


@pytest.mark.respx(base_url=base_url)
def test_whoami_retries_once_after_401_with_refreshed_token(
    respx_mock: MockRouter,
    cli_runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from together.lib.cli.auth import TogetherAuth, StoredCredentials, save_stored_credentials

    creds = tmp_path / "credentials.json"
    monkeypatch.setenv("TOGETHER_CREDENTIALS_PATH", str(creds))
    save_stored_credentials(StoredCredentials(access_token="revoked-jwt", refresh_token="rt", issuer=base_url))
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds)
    forced: list[bool] = []

    def fake_refresh(_self: TogetherAuth, *, force: bool = False, **_kwargs: object) -> StoredCredentials | None:
        forced.append(force)
        if not force:
            # Command start: the token is not expired, so nothing to refresh.
            return None
        updated = StoredCredentials(access_token="fresh-jwt", refresh_token="rt")
        save_stored_credentials(updated)
        return updated

    monkeypatch.setattr(TogetherAuth, "refresh", fake_refresh)
    seen: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.headers.get("authorization"))
        if request.headers.get("authorization") != "Bearer fresh-jwt":
            return httpx.Response(401, json={"error": {"message": "unauthorized"}})
        return httpx.Response(200, json=_whoami_body())

    respx_mock.get("/v3/whoami").mock(side_effect=handler)
    result = cli_runner.invoke(["whoami", "--json"])
    assert result.exit_code == 0, result.output
    assert seen == ["Bearer revoked-jwt", "Bearer fresh-jwt"]
    assert forced == [False, True]


def test_whoami_calls_the_stored_issuer_environment(
    respx_mock: MockRouter,
    cli_runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from together.lib.cli.auth import StoredCredentials, save_stored_credentials

    creds = tmp_path / "credentials.json"
    monkeypatch.setenv("TOGETHER_CREDENTIALS_PATH", str(creds))
    save_stored_credentials(StoredCredentials(access_token="stored-jwt", issuer="https://api.qa.together.ai/"))
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds)
    cli_runner.env["TOGETHER_BASE_URL"] = "http://127.0.0.1:9"

    route = respx_mock.get("https://api.qa.together.ai/v3/whoami").mock(
        return_value=httpx.Response(200, json=_whoami_body())
    )
    result = cli_runner.invoke(["whoami", "--json"])
    assert result.exit_code == 0, result.output
    assert route.called


def test_whoami_base_url_flag_rejected_when_logged_in(
    cli_runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from together.lib.cli.auth import StoredCredentials, save_stored_credentials

    creds = tmp_path / "credentials.json"
    monkeypatch.setenv("TOGETHER_CREDENTIALS_PATH", str(creds))
    save_stored_credentials(StoredCredentials(access_token="stored-jwt", issuer="https://api.qa.together.ai"))
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds)

    result = cli_runner.invoke(["--base-url", "https://flag.example.com/v1", "whoami", "--json"])
    assert result.exit_code == 1, result.output
    assert json.loads(result.output)["error"] == (
        "Cannot set --base-url while logged in. This session uses the issuer from `tg login`."
    )


@pytest.mark.respx(base_url=base_url)
@pytest.mark.parametrize(
    ("body", "present", "absent"),
    [
        (
            {
                "type": "org_api_key",
                "api_key": {"id": "key-1"},
                "organization": {"id": "org-1", "name": "Acme Org"},
            },
            ["key-1", "Acme Org", "org-1"],
            ["Project:"],
        ),
        (
            {"type": "user_jwt", "user": {"id": "user-1"}},
            ["user-1"],
            ["Project:", "Organization:", "API key:"],
        ),
        (
            {
                "type": "user_org_jwt",
                "user": {"id": "user-1"},
                "organization": {"id": "org-1", "name": "Acme Org"},
            },
            ["user-1", "Acme Org", "org-1"],
            ["Project:", "API key:"],
        ),
        (
            {
                "type": "user_org_project_jwt",
                "user": {"id": "user-1"},
                "organization": {"id": "org-1", "name": "Acme Org"},
                "project": {"id": "proj", "name": "My Project", "slug": "my-project"},
            },
            ["user-1", "Acme Org", "org-1", "My Project", "proj"],
            ["API key:"],
        ),
    ],
)
def test_whoami_renders_each_v3_variant(
    respx_mock: MockRouter,
    cli_runner: CliRunner,
    body: dict[str, object],
    present: list[str],
    absent: list[str],
) -> None:
    respx_mock.get("/v3/whoami").mock(return_value=httpx.Response(200, json=body))

    human = cli_runner.invoke(["whoami"])
    assert human.exit_code == 0, human.output
    for text in present:
        assert text in human.output
    for text in absent:
        assert text not in human.output

    dumped = cli_runner.invoke(["whoami", "--json"])
    assert dumped.exit_code == 0, dumped.output
    payload = json.loads(dumped.output)
    assert payload["type"] == body["type"]
