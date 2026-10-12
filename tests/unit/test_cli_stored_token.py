"""Launcher skips project-resolution whoami() when auth is a `tg login` token."""

from __future__ import annotations

import os
from typing import Any
from pathlib import Path

import pytest

import together.lib.cli as cli
from together.lib.cli.auth import StoredCredentials, save_stored_credentials


def _run(argv: list[str]) -> None:
    try:
        cli.app.meta(argv)
    except SystemExit:
        pass
    except Exception:
        pass


def _spy_resolve(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    calls = [0]

    async def spy_resolve(_client: object) -> str:
        calls[0] += 1
        return "proj"

    monkeypatch.setattr(cli, "_resolve_project_id", spy_resolve)
    return calls


def test_stored_access_token_skips_project_resolution_whoami(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    creds = tmp_path / "credentials.json"
    monkeypatch.setenv("TOGETHER_CREDENTIALS_PATH", str(creds))
    monkeypatch.setenv("TOGETHER_API_KEY", "env-key-should-not-force-whoami")
    monkeypatch.delenv("TOGETHER_PROJECT_ID", raising=False)
    monkeypatch.setenv("TOGETHER_BASE_URL", "http://127.0.0.1:4010")
    monkeypatch.setenv("TOGETHER_DISABLE_VERSION_CHECK", "1")
    save_stored_credentials(StoredCredentials(access_token="stored-jwt"))

    calls = _spy_resolve(monkeypatch)
    _run(["telemetry", "status"])
    assert calls[0] == 0


def test_env_api_key_still_resolves_project_via_whoami(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TOGETHER_CREDENTIALS_PATH", str(tmp_path / "missing-credentials.json"))
    monkeypatch.setenv("TOGETHER_API_KEY", "env-key")
    monkeypatch.delenv("TOGETHER_PROJECT_ID", raising=False)
    monkeypatch.setenv("TOGETHER_BASE_URL", "http://127.0.0.1:4010")
    monkeypatch.setenv("TOGETHER_DISABLE_VERSION_CHECK", "1")

    calls = _spy_resolve(monkeypatch)
    _run(["telemetry", "status"])
    assert calls[0] == 1


def test_explicit_api_key_still_resolves_project_via_whoami(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    creds = tmp_path / "credentials.json"
    monkeypatch.setenv("TOGETHER_CREDENTIALS_PATH", str(creds))
    monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
    monkeypatch.delenv("TOGETHER_PROJECT_ID", raising=False)
    monkeypatch.setenv("TOGETHER_BASE_URL", "http://127.0.0.1:4010")
    monkeypatch.setenv("TOGETHER_DISABLE_VERSION_CHECK", "1")
    save_stored_credentials(StoredCredentials(access_token="stored-jwt"))

    calls = _spy_resolve(monkeypatch)
    _run(["--api-key", "flag-key", "telemetry", "status"])
    assert calls[0] == 1


def test_logged_in_ignores_together_base_url(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    creds = tmp_path / "credentials.json"
    monkeypatch.setenv("TOGETHER_CREDENTIALS_PATH", str(creds))
    monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
    monkeypatch.delenv("TOGETHER_PROJECT_ID", raising=False)
    monkeypatch.setenv("TOGETHER_BASE_URL", "http://127.0.0.1:9")
    monkeypatch.setenv("TOGETHER_DISABLE_VERSION_CHECK", "1")
    save_stored_credentials(StoredCredentials(access_token="stored-jwt", issuer="https://api.qa.together.ai"))

    seen: list[tuple[str, bool]] = []
    real_create = cli._create_client

    def spy_create(*args: Any, **kwargs: Any) -> object:
        client, missing = real_create(*args, **kwargs)
        seen.append((str(client.base_url), bool(client._base_url_overridden)))
        return client, missing

    monkeypatch.setattr(cli, "_create_client", spy_create)
    _spy_resolve(monkeypatch)
    _run(["telemetry", "status"])
    assert seen == [("https://api.qa.together.ai/v1/", True)]
    assert os.environ["TOGETHER_BASE_URL"] == "http://127.0.0.1:9"


def test_logged_in_production_keeps_default_routing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    creds = tmp_path / "credentials.json"
    monkeypatch.setenv("TOGETHER_CREDENTIALS_PATH", str(creds))
    monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
    monkeypatch.delenv("TOGETHER_PROJECT_ID", raising=False)
    monkeypatch.setenv("TOGETHER_BASE_URL", "http://127.0.0.1:9")
    monkeypatch.setenv("TOGETHER_DISABLE_VERSION_CHECK", "1")
    save_stored_credentials(StoredCredentials(access_token="stored-jwt", issuer="https://api.together.ai"))

    seen: list[tuple[str, bool]] = []
    real_create = cli._create_client

    def spy_create(*args: Any, **kwargs: Any) -> object:
        client, missing = real_create(*args, **kwargs)
        seen.append((str(client.base_url), bool(client._base_url_overridden)))
        return client, missing

    monkeypatch.setattr(cli, "_create_client", spy_create)
    _spy_resolve(monkeypatch)
    _run(["telemetry", "status"])
    assert seen == [("https://api.together.ai/v1/", False)]


def test_stored_project_id_is_applied_to_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    creds = tmp_path / "credentials.json"
    monkeypatch.setenv("TOGETHER_CREDENTIALS_PATH", str(creds))
    monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
    monkeypatch.delenv("TOGETHER_PROJECT_ID", raising=False)
    monkeypatch.setenv("TOGETHER_BASE_URL", "http://127.0.0.1:4010")
    monkeypatch.setenv("TOGETHER_DISABLE_VERSION_CHECK", "1")
    save_stored_credentials(StoredCredentials(access_token="parent-jwt", refresh_token="rt"))
    save_stored_credentials(StoredCredentials(access_token="child-jwt", project_id="proj_switched"))

    seen: list[str | None] = []
    real_create = cli._create_client

    def spy_create(
        api_key: object,
        base_url: object,
        timeout: object,
        max_retries: object,
        project_id: object,
        **kwargs: Any,
    ) -> object:
        seen.append(project_id if isinstance(project_id, str) or project_id is None else str(project_id))
        return real_create(
            api_key,  # type: ignore[arg-type]
            base_url,  # type: ignore[arg-type]
            timeout,  # type: ignore[arg-type]
            max_retries,  # type: ignore[arg-type]
            project_id,  # type: ignore[arg-type]
            **kwargs,
        )

    monkeypatch.setattr(cli, "_create_client", spy_create)
    _spy_resolve(monkeypatch)
    _run(["telemetry", "status"])
    assert seen == ["proj_switched"]
