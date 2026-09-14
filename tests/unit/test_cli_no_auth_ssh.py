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

    require_flags: list[bool] = []
    resolve_calls = 0

    real_create = cli._create_client

    def spy_create(*args: object, require_api_key: bool = True, **kwargs: object):  # type: ignore[no-untyped-def]
        require_flags.append(require_api_key)
        return real_create(*args, require_api_key=require_api_key, **kwargs)  # type: ignore[arg-type]

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

    # The client is built with the api-key requirement waived (no hard exit on a
    # missing key) and the project-resolution whoami() is skipped entirely.
    assert require_flags == [False], "ssh must build the client with require_api_key=False"
    assert resolve_calls == 0, "ssh must not run the project-resolution whoami()"


def test_non_ssh_command_still_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TOGETHER_API_KEY", raising=False)

    require_flags: list[bool] = []
    real_create = cli._create_client

    def spy_create(*args: object, require_api_key: bool = True, **kwargs: object):  # type: ignore[no-untyped-def]
        require_flags.append(require_api_key)
        return real_create(*args, require_api_key=require_api_key, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(cli, "_create_client", spy_create)

    # Pass --project so launcher skips whoami(); otherwise the missing-key request
    # hook fires mid-connect and leaves an unclosed socket (filterwarnings=error).
    _run(["endpoints", "list", "--project", "proj"])

    assert require_flags and all(require_flags), "API-backed commands must still gate on the API key"
