from __future__ import annotations

import json
import stat
from pathlib import Path

import pytest

from together import Together, TogetherError
from tests.cli.utils import stored_project_id, stored_access_token
from together.lib.cli.auth import (
    CredentialStore,
    StoredCredentials,
    credentials_path,
    load_stored_base_url,
    load_stored_credentials,
    save_stored_credentials,
)


@pytest.fixture
def creds_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "credentials.json"
    monkeypatch.setenv("TOGETHER_CREDENTIALS_PATH", str(path))
    monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
    return path


def test_save_and_load_round_trip(creds_file: Path) -> None:
    saved = save_stored_credentials(
        StoredCredentials(
            access_token="jwt-access",
            refresh_token="refresh-1",
            issuer="https://api.together.ai",
            expires_at=1_700_000_000,
            client_id="together-cli",
        )
    )
    assert saved == creds_file
    assert stat.S_IMODE(creds_file.stat().st_mode) == 0o600
    loaded = load_stored_credentials()
    assert loaded is not None
    assert loaded.access_token == "jwt-access"
    assert loaded.refresh_token == "refresh-1"
    assert loaded.issuer == "https://api.together.ai"
    assert loaded.client_id == "together-cli"
    assert loaded.project_id is None
    assert stored_access_token() == "jwt-access"


def test_load_missing_and_invalid(creds_file: Path) -> None:
    assert load_stored_credentials() is None
    creds_file.write_text("{not-json", encoding="utf-8")
    assert load_stored_credentials() is None
    creds_file.write_text(json.dumps({"token_type": "Bearer"}), encoding="utf-8")
    assert load_stored_credentials() is None


def test_saving_an_empty_store_deletes_the_file(creds_file: Path) -> None:
    save_stored_credentials(StoredCredentials(access_token="jwt-access"))
    assert creds_file.exists()
    CredentialStore(credentials=[]).save()
    assert not creds_file.exists()


def test_credentials_path_uses_xdg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TOGETHER_CREDENTIALS_PATH", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    assert credentials_path() == tmp_path / "xdg" / "together" / "credentials.json"


def test_current_entry_is_the_stored_token(creds_file: Path) -> None:
    save_stored_credentials(StoredCredentials(access_token="parent-jwt", refresh_token="rt"))
    assert stored_access_token() == "parent-jwt"
    save_stored_credentials(StoredCredentials(access_token="child-jwt", project_id="proj_1"))
    assert creds_file.is_file()
    assert stored_access_token() == "child-jwt"
    assert stored_project_id() == "proj_1"


@pytest.mark.usefixtures("creds_file")
def test_sdk_client_does_not_read_the_credential_store(monkeypatch: pytest.MonkeyPatch) -> None:
    # `tg login` credentials are a CLI concern; the SDK only uses TOGETHER_API_KEY / api_key.
    monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
    monkeypatch.delenv("TOGETHER_BASE_URL", raising=False)
    save_stored_credentials(StoredCredentials(access_token="stored-jwt", issuer="https://api.qa.together.ai"))
    with pytest.raises(TogetherError, match="api_key"):
        Together()
    assert str(Together(api_key="explicit-key").base_url) == "https://api.together.ai"


def test_file_is_kubeconfig_shaped(creds_file: Path) -> None:
    save_stored_credentials(StoredCredentials(access_token="parent-jwt", refresh_token="rt"))
    save_stored_credentials(StoredCredentials(access_token="child-jwt", project_id="proj_1"))
    data = json.loads(creds_file.read_text(encoding="utf-8"))
    assert data["version"] == 1
    assert data["current"] == "proj_1"
    assert [entry["name"] for entry in data["credentials"]] == ["default", "proj_1"]
    assert "access_token" not in data
    # The project entry is not merged with the login entry.
    assert data["credentials"][1] == {
        "name": "proj_1",
        "access_token": "child-jwt",
        "project_id": "proj_1",
        "token_type": "Bearer",
    }


def test_current_pointer_selects_among_legacy_entries(creds_file: Path) -> None:
    creds_file.write_text(
        json.dumps(
            {
                "version": 1,
                "current": "proj_2",
                "credentials": [
                    {"name": "default", "access_token": "parent-jwt"},
                    {
                        "name": "proj_1",
                        "access_token": "parent-jwt",
                        "project_id": "proj_1",
                        "project_access_token": "one",
                    },
                    {
                        "name": "proj_2",
                        "access_token": "parent-jwt",
                        "project_id": "proj_2",
                        "project_access_token": "two",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    assert stored_access_token() == "two"
    assert stored_project_id() == "proj_2"


@pytest.mark.usefixtures("creds_file")
def test_upsert_replaces_entry_with_same_name() -> None:
    save_stored_credentials(StoredCredentials(access_token="old", project_id="proj_1"))
    save_stored_credentials(StoredCredentials(access_token="p"))
    save_stored_credentials(StoredCredentials(access_token="new", project_id="proj_1"))
    store = CredentialStore.load()
    assert [entry.entry_name for entry in store.credentials] == ["default", "proj_1"]
    assert store.current == "proj_1"
    assert stored_access_token() == "new"


def test_unknown_current_means_not_logged_in(creds_file: Path) -> None:
    creds_file.write_text(
        json.dumps({"current": "missing", "credentials": [{"name": "default", "access_token": "jwt"}]}),
        encoding="utf-8",
    )
    assert load_stored_credentials() is None
    assert stored_access_token() is None


def test_legacy_flat_file_is_read_as_default_entry(creds_file: Path) -> None:
    creds_file.write_text(json.dumps({"access_token": "parent", "refresh_token": "rt"}), encoding="utf-8")
    store = CredentialStore.load()
    assert store.current == "default"
    assert stored_access_token() == "parent"
    # The next write migrates the file to the new shape.
    save_stored_credentials(StoredCredentials(access_token="c2", project_id="proj_2"))
    data = json.loads(creds_file.read_text(encoding="utf-8"))
    assert [entry["name"] for entry in data["credentials"]] == ["default", "proj_2"]
    assert data["current"] == "proj_2"


def test_legacy_flat_merged_file_is_split(creds_file: Path) -> None:
    creds_file.write_text(
        json.dumps(
            {
                "access_token": "parent",
                "refresh_token": "rt",
                "issuer": "https://api.together.ai",
                "project_id": "proj_1",
                "project_access_token": "child",
                "project_expires_at": 1_700_000_100,
            }
        ),
        encoding="utf-8",
    )
    store = CredentialStore.load()
    assert store.current == "proj_1"
    login, project = store.credentials
    assert (login.entry_name, login.access_token, login.refresh_token, login.project_id) == (
        "default",
        "parent",
        "rt",
        None,
    )
    assert (project.entry_name, project.access_token, project.refresh_token, project.expires_at) == (
        "proj_1",
        "child",
        None,
        1_700_000_100,
    )
    assert project.issuer == "https://api.together.ai"
    assert stored_access_token() == "child"


def test_legacy_merged_list_entries_are_split(creds_file: Path) -> None:
    creds_file.write_text(
        json.dumps(
            {
                "version": 1,
                "current": "proj_1",
                "credentials": [
                    {"name": "default", "access_token": "parent", "refresh_token": "rt"},
                    {
                        "name": "proj_1",
                        "access_token": "parent",
                        "refresh_token": "rt",
                        "project_id": "proj_1",
                        "project_access_token": "child",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    store = CredentialStore.load()
    assert [entry.entry_name for entry in store.credentials] == ["default", "proj_1"]
    project = store.get("proj_1")
    assert project is not None
    assert project.access_token == "child"
    assert project.refresh_token is None
    login = store.login_credentials()
    assert login is not None and login.entry_name == "default"


@pytest.mark.parametrize(
    ("issuer", "base_url"),
    [
        ("https://api.qa.together.ai/", "https://api.qa.together.ai"),
        # Production maps to None so the SDK default applies.
        ("https://api.together.ai", None),
        (None, None),
    ],
)
@pytest.mark.usefixtures("creds_file")
def test_load_stored_base_url(issuer: "str | None", base_url: "str | None") -> None:
    save_stored_credentials(StoredCredentials(access_token="stored-jwt", issuer=issuer))
    assert load_stored_base_url() == base_url


@pytest.mark.usefixtures("creds_file")
def test_no_stored_base_url_without_credentials() -> None:
    assert load_stored_base_url() is None
