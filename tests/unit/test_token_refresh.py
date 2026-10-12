from __future__ import annotations

from typing import Any, Optional
from pathlib import Path
from dataclasses import replace

import httpx
import pytest

from together import TogetherError
from tests.cli.utils import stored_access_token
from together.lib.cli.auth import (
    TogetherAuth,
    CredentialStore,
    StoredTokenAuth,
    StoredCredentials,
    save_stored_credentials,
)

NOW = 1_800_000_000


@pytest.fixture
def creds_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "credentials.json"
    monkeypatch.setenv("TOGETHER_CREDENTIALS_PATH", str(path))
    return path


def _discovery() -> dict[str, Any]:
    return {
        "issuer": "https://api.together.ai",
        "authorization_endpoint": "https://api.together.ai/oauth/authorize",
        "token_endpoint": "https://api.together.ai/oauth/token",
    }


def _parent(**overrides: Any) -> StoredCredentials:
    fields: dict[str, Any] = {
        "access_token": "parent-old",
        "refresh_token": "rt-old",
        "expires_at": NOW + 3600,
        "issuer": "https://api.together.ai",
        "client_id": "together-cli",
    }
    fields.update(overrides)
    return StoredCredentials(**fields)


class _TokenServer:
    def __init__(
        self,
        *,
        refresh_status: int = 200,
        refresh_body: Optional[dict[str, Any]] = None,
        exchange_status: int = 200,
        session_status: int = 200,
        session_error: str = "invalid_grant",
    ) -> None:
        self.grants: list[dict[str, str]] = []
        self.exchange_status = exchange_status
        self.session_status = session_status
        self.session_error = session_error
        self.refresh_status = refresh_status
        self.refresh_body = refresh_body or {
            "access_token": "parent-new",
            "refresh_token": "rt-new",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

    def handler(self, request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=_discovery())
        form = dict(httpx.QueryParams(request.content.decode()))
        self.grants.append(form)
        if form["grant_type"] == "refresh_token":
            return httpx.Response(self.refresh_status, json=self.refresh_body)
        if form["grant_type"] == _SESSION:
            if self.session_status != 200:
                return httpx.Response(
                    self.session_status,
                    json={"error": self.session_error, "error_description": "session is no longer live"},
                )
            return httpx.Response(
                200, json={"access_token": f"renewed-{form['access_token']}", "token_type": "Bearer", "expires_in": 900}
            )
        if self.exchange_status != 200:
            return httpx.Response(
                self.exchange_status, json={"error": "server_error", "error_description": "Token exchange failed"}
            )
        return httpx.Response(
            200, json={"access_token": f"child-for-{form['subject_token']}", "token_type": "Bearer", "expires_in": 600}
        )

    def refresh(self, **kwargs: Any) -> Optional[StoredCredentials]:
        with httpx.Client(transport=httpx.MockTransport(self.handler)) as client:
            return TogetherAuth(http_client=client, clock=lambda: NOW).refresh(**kwargs)


@pytest.mark.usefixtures("creds_file")
def test_fresh_tokens_are_not_refreshed() -> None:
    save_stored_credentials(_parent())
    server = _TokenServer()
    assert server.refresh() is None
    assert server.grants == []


@pytest.mark.usefixtures("creds_file")
def test_expired_parent_is_refreshed_and_persisted() -> None:
    save_stored_credentials(_parent(expires_at=NOW + 30))
    server = _TokenServer()
    updated = server.refresh()
    assert updated is not None
    assert [g["grant_type"] for g in server.grants] == ["refresh_token"]
    assert server.grants[0]["refresh_token"] == "rt-old"
    assert server.grants[0]["access_token"] == "parent-old"
    assert server.grants[0]["client_id"] == "together-cli"
    assert stored_access_token() == "parent-new"
    stored = CredentialStore.load().current_credentials()
    assert stored is not None
    assert stored.refresh_token == "rt-new"
    assert stored.expires_at == NOW + 3600


@pytest.mark.usefixtures("creds_file")
def test_refresh_keeps_refresh_token_when_not_rotated() -> None:
    save_stored_credentials(_parent(expires_at=NOW - 1))
    server = _TokenServer(refresh_body={"access_token": "parent-new", "expires_in": 3600})
    server.refresh()
    stored = CredentialStore.load().current_credentials()
    assert stored is not None
    assert stored.refresh_token == "rt-old"


_SESSION = "urn:together.ai:params:oauth:grant-type:session"


def _project(**overrides: Any) -> StoredCredentials:
    fields: dict[str, Any] = {
        "access_token": "child-old",
        "expires_at": NOW + 600,
        "issuer": "https://api.together.ai",
        "client_id": "together-cli",
        "project_id": "proj_1",
    }
    fields.update(overrides)
    return StoredCredentials(**fields)


def _switched(*, login: Optional[StoredCredentials] = None, project: Optional[StoredCredentials] = None) -> None:
    save_stored_credentials(login or _parent())
    save_stored_credentials(project or _project())


@pytest.mark.usefixtures("creds_file")
def test_expired_project_token_is_renewed_with_the_session_grant() -> None:
    _switched(project=_project(expires_at=NOW - 1))
    server = _TokenServer()
    updated = server.refresh()
    assert server.grants == [{"grant_type": _SESSION, "access_token": "child-old", "client_id": "together-cli"}]
    assert updated is not None
    store = CredentialStore.load()
    assert store.current == "proj_1"
    assert store.get("proj_1") == replace(
        _project(), access_token="renewed-child-old", expires_at=NOW + 900, name="proj_1"
    )
    # The login entry is not used or touched.
    assert store.get("default") == replace(_parent(), name="default")
    assert stored_access_token() == "renewed-child-old"


@pytest.mark.usefixtures("creds_file")
def test_session_grant_does_not_need_or_refresh_the_login() -> None:
    save_stored_credentials(_project(expires_at=NOW - 1))
    server = _TokenServer()
    server.refresh()
    assert [g["grant_type"] for g in server.grants] == [_SESSION]
    assert stored_access_token() == "renewed-child-old"


@pytest.mark.usefixtures("creds_file")
def test_expired_login_is_not_refreshed_for_a_project_entry() -> None:
    _switched(login=_parent(expires_at=NOW - 1), project=_project(expires_at=NOW - 1))
    server = _TokenServer()
    server.refresh()
    assert [g["grant_type"] for g in server.grants] == [_SESSION]
    login = CredentialStore.load().get("default")
    assert login is not None and login.access_token == "parent-old"


@pytest.mark.usefixtures("creds_file")
def test_force_on_project_entry_uses_the_session_grant() -> None:
    _switched()
    server = _TokenServer()
    server.refresh(force=True)
    assert [g["grant_type"] for g in server.grants] == [_SESSION]
    assert server.grants[0]["access_token"] == "child-old"


@pytest.mark.usefixtures("creds_file")
def test_dead_project_session_asks_for_switch_and_keeps_token() -> None:
    _switched(project=_project(expires_at=NOW - 1))
    server = _TokenServer(session_status=400)
    with pytest.raises(TogetherError, match="tg switch proj_1"):
        server.refresh()
    assert stored_access_token() == "child-old"


@pytest.mark.usefixtures("creds_file")
def test_failed_session_grant_names_the_step() -> None:
    _switched(project=_project(expires_at=NOW - 1))
    server = _TokenServer(session_status=400, session_error="unsupported_grant_type")
    with pytest.raises(TogetherError, match="Project token refresh failed \\(unsupported_grant_type\\)"):
        server.refresh()


@pytest.mark.usefixtures("creds_file")
def test_project_entry_ignores_expired_login_while_project_token_is_fresh() -> None:
    _switched(login=_parent(expires_at=NOW - 1))
    server = _TokenServer()
    assert server.refresh() is None
    assert server.grants == []


@pytest.mark.usefixtures("creds_file")
def test_login_refresh_leaves_project_entries_alone() -> None:
    save_stored_credentials(_project())
    save_stored_credentials(_parent(expires_at=NOW - 1))
    _TokenServer().refresh()
    store = CredentialStore.load()
    assert store.current == "default"
    assert store.get("proj_1") == replace(_project(), name="proj_1")
    assert stored_access_token() == "parent-new"


@pytest.mark.usefixtures("creds_file")
def test_refresh_by_name_targets_that_entry() -> None:
    _switched(login=_parent(expires_at=NOW - 1))
    server = _TokenServer()
    server.refresh(name="default")
    assert [g["grant_type"] for g in server.grants] == ["refresh_token"]
    assert CredentialStore.load().current == "proj_1"
    assert stored_access_token() == "child-old"


@pytest.mark.usefixtures("creds_file")
def test_rejected_refresh_asks_for_login() -> None:
    save_stored_credentials(_parent(expires_at=NOW - 1))
    server = _TokenServer(refresh_status=400, refresh_body={"error": "invalid_grant"})
    with pytest.raises(TogetherError, match="tg login"):
        server.refresh()
    assert stored_access_token() == "parent-old"


def test_nothing_to_refresh_without_credentials(creds_file: Path) -> None:
    assert not creds_file.exists()
    assert _TokenServer().refresh(force=True) is None


class _Api:
    def __init__(self, *, valid: str) -> None:
        self.valid = valid
        self.seen: list[Optional[str]] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.seen.append(request.headers.get("authorization"))
        if request.headers.get("authorization") == f"Bearer {self.valid}":
            return httpx.Response(200, json={"ok": True})
        return httpx.Response(401, json={"error": "unauthorized"})


def _auth(token: str, new_token: Optional[str], calls: list[int], tokens: list[str]) -> StoredTokenAuth:
    def refresh() -> Optional[StoredCredentials]:
        calls.append(1)
        return None if new_token is None else StoredCredentials(access_token=new_token)

    return StoredTokenAuth(token, tokens.append, refresh=refresh)


async def test_401_refreshes_once_and_retries() -> None:
    api = _Api(valid="fresh")
    calls: list[int] = []
    tokens: list[str] = []
    auth = _auth("stale", "fresh", calls, tokens)
    async with httpx.AsyncClient(transport=httpx.MockTransport(api.handler), auth=auth) as client:
        first = await client.get("https://api.together.ai/v1/models", headers={"Authorization": "Bearer stale"})
        # A request built before the refresh still carries the stale token; retry it without refreshing again.
        second = await client.get("https://api.together.ai/v1/models", headers={"Authorization": "Bearer stale"})
    assert first.status_code == 200
    assert second.status_code == 200
    assert api.seen == ["Bearer stale", "Bearer fresh", "Bearer stale", "Bearer fresh"]
    assert calls == [1]
    assert tokens == ["fresh"]


async def test_401_after_refresh_is_returned() -> None:
    api = _Api(valid="never")
    calls: list[int] = []
    auth = _auth("stale", "still-bad", calls, [])
    async with httpx.AsyncClient(transport=httpx.MockTransport(api.handler), auth=auth) as client:
        response = await client.get("https://api.together.ai/v1/models", headers={"Authorization": "Bearer stale"})
    assert response.status_code == 401
    assert api.seen == ["Bearer stale", "Bearer still-bad"]
    assert calls == [1]


async def test_401_when_refresh_unavailable_is_returned() -> None:
    api = _Api(valid="fresh")
    calls: list[int] = []
    auth = _auth("stale", None, calls, [])
    async with httpx.AsyncClient(transport=httpx.MockTransport(api.handler), auth=auth) as client:
        response = await client.get("https://api.together.ai/v1/models", headers={"Authorization": "Bearer stale"})
    assert response.status_code == 401
    assert calls == [1]
    assert auth.refresh_failure is None


async def test_401_records_a_rejected_refresh() -> None:
    api = _Api(valid="fresh")
    expired = TogetherError("Login expired. Run `tg login` and try again.")

    def refresh() -> Optional[StoredCredentials]:
        raise expired

    auth = StoredTokenAuth("stale", lambda _token: None, refresh=refresh)
    async with httpx.AsyncClient(transport=httpx.MockTransport(api.handler), auth=auth) as client:
        response = await client.get("https://api.together.ai/v1/models", headers={"Authorization": "Bearer stale"})
    assert response.status_code == 401
    assert auth.refresh_failure is expired
    assert api.seen == ["Bearer stale"]


async def test_401_for_other_credentials_is_not_refreshed() -> None:
    api = _Api(valid="fresh")
    calls: list[int] = []
    auth = _auth("stale", "fresh", calls, [])
    async with httpx.AsyncClient(transport=httpx.MockTransport(api.handler), auth=auth) as client:
        response = await client.put("https://uploads.example.com/presigned", content=b"data")
    assert response.status_code == 401
    assert calls == []


def test_sync_401_refreshes_once_and_retries() -> None:
    api = _Api(valid="fresh")
    calls: list[int] = []
    auth = _auth("stale", "fresh", calls, [])
    with httpx.Client(transport=httpx.MockTransport(api.handler), auth=auth) as client:
        response = client.get("https://api.together.ai/v1/models", headers={"Authorization": "Bearer stale"})
    assert response.status_code == 200
    assert calls == [1]


@pytest.mark.usefixtures("creds_file")
def test_refresh_uses_stored_issuer_over_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TOGETHER_ISSUER", "https://api.together.ai")
    qa = "https://api.qa.together.ai"
    save_stored_credentials(_parent(issuer=qa))
    hosts: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        hosts.append(request.url.host)
        if request.url.path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(
                200,
                json={
                    "issuer": qa,
                    "authorization_endpoint": f"{qa}/oauth/authorize",
                    "token_endpoint": f"{qa}/oauth/token",
                },
            )
        return httpx.Response(200, json={"access_token": "parent-new", "refresh_token": "rt-new", "expires_in": 3600})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        updated = TogetherAuth(http_client=client, clock=lambda: NOW).refresh(force=True)

    assert hosts == ["api.qa.together.ai", "api.qa.together.ai"]
    assert updated is not None and updated.issuer == qa


@pytest.mark.usefixtures("creds_file")
def test_refresh_without_stored_issuer_sends_nothing() -> None:
    save_stored_credentials(_parent(issuer=None, expires_at=NOW - 1))
    server = _TokenServer()
    with pytest.raises(TogetherError, match="do not record their issuer"):
        server.refresh()
    assert server.grants == []
    assert stored_access_token() == "parent-old"
