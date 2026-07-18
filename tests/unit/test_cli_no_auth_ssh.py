"""Regression: `tg beta clusters ssh` authenticates via OIDC/step-ca and must not
be gated on an API key or the launcher's up-front whoami() (project resolution).

Guards against reintroducing the #25 behavior where every command — including the
keyless ssh command — triggered `_create_client` + `_resolve_project_id`.
"""

from __future__ import annotations

import pytest

import together.lib.cli as cli


def _run(argv: list[str]) -> None:
    try:
        cli.app.meta(argv)
    except SystemExit:
        pass
    except Exception:
        # ssh proceeds past auth into OIDC discovery / ssh exec, which fails in a
        # unit test (no network / no login). That's fine — we only assert the
        # launcher never touched the API client for this command.
        pass


def test_ssh_command_does_not_require_api_key_or_whoami(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TOGETHER_API_KEY", raising=False)

    create_calls = 0
    resolve_calls = 0

    real_create = cli._create_client

    def spy_create(*args: object, **kwargs: object):  # type: ignore[no-untyped-def]
        nonlocal create_calls
        create_calls += 1
        return real_create(*args, **kwargs)  # type: ignore[arg-type]

    async def spy_resolve(_client: object) -> str:
        nonlocal resolve_calls
        resolve_calls += 1
        return "proj"

    monkeypatch.setattr(cli, "_create_client", spy_create)
    monkeypatch.setattr(cli, "_resolve_project_id", spy_resolve)

    _run(
        [
            "beta",
            "clusters",
            "ssh",
            "https://dex.together.ai/abc",
            "-l",
            "me",
            "--host",
            "host",
            "--ssh-config-alias",
            "x",
        ]
    )

    assert create_calls == 0, "ssh must not construct an API client (no api-key gate)"
    assert resolve_calls == 0, "ssh must not run the project-resolution whoami()"


def test_non_ssh_command_still_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TOGETHER_API_KEY", raising=False)

    create_calls = 0
    real_create = cli._create_client

    def spy_create(*args: object, **kwargs: object):  # type: ignore[no-untyped-def]
        nonlocal create_calls
        create_calls += 1
        return real_create(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(cli, "_create_client", spy_create)

    _run(["endpoints", "list"])

    assert create_calls >= 1, "API-backed commands must still construct the client / gate on the key"
