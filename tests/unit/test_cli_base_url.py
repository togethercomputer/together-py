"""CLI rejects legacy `/v1` base URLs via the normal Error: / exit path."""

from __future__ import annotations

from typing import Optional

import httpx
import pytest

import together.lib.cli as cli
from together import NotFoundError


@pytest.mark.parametrize(
    ("env_url", "flag_url", "source", "root"),
    [
        ("https://staging.together.ai/v1/", None, "TOGETHER_BASE_URL", "https://staging.together.ai"),
        (None, "https://api.together.ai/v1", "--base-url", "https://api.together.ai"),
        # Query/fragment must not fool a string endswith("/v1") check; share auth's urlparse path.
        (None, "https://api.together.ai/v1?x=1", "--base-url", "https://api.together.ai"),
        ("https://gw.together.ai/prefix/v1/", None, "TOGETHER_BASE_URL", "https://gw.together.ai/prefix"),
    ],
)
def test_create_client_rejects_legacy_v1_base_url(
    monkeypatch: pytest.MonkeyPatch,
    env_url: Optional[str],
    flag_url: Optional[str],
    source: str,
    root: str,
) -> None:
    monkeypatch.setenv("TOGETHER_API_KEY", "key")
    monkeypatch.delenv("TOGETHER_BASE_URL", raising=False)
    if env_url is not None:
        monkeypatch.setenv("TOGETHER_BASE_URL", env_url)

    with pytest.raises(ValueError, match=rf"Set {source} to {root}\.") as exc_info:
        cli._create_client(api_key=None, base_url=flag_url, timeout=None, max_retries=None, project_id=None)

    assert "without /v1" in str(exc_info.value)


def test_create_client_ignores_relative_legacy_v1(monkeypatch: pytest.MonkeyPatch) -> None:
    """Relative URLs are rejected by api_root_from_base_url; don't invent a strip via string ops."""
    monkeypatch.setenv("TOGETHER_API_KEY", "key")
    monkeypatch.delenv("TOGETHER_BASE_URL", raising=False)

    client, _ = cli._create_client(
        api_key=None, base_url="api.together.ai/v1", timeout=None, max_retries=None, project_id=None
    )

    assert "v1" in str(client.base_url)


def test_create_client_accepts_api_root(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TOGETHER_API_KEY", "key")
    monkeypatch.setenv("TOGETHER_BASE_URL", "http://127.0.0.1:4010")

    client, _ = cli._create_client(api_key=None, base_url=None, timeout=None, max_retries=None, project_id=None)

    assert str(client.base_url).rstrip("/") == "http://127.0.0.1:4010"


def test_legacy_v1_base_url_exits_via_normal_error_handling(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("TOGETHER_API_KEY", "key")
    monkeypatch.setenv("TOGETHER_BASE_URL", "https://api.together.ai/v1")
    monkeypatch.setattr(cli, "load_stored_credentials", lambda: None)
    monkeypatch.setattr(cli, "flush_pending_events", lambda: None)
    monkeypatch.setattr(cli, "track_cli", lambda *_args, **_kwargs: None)

    with pytest.raises(SystemExit) as exc_info:
        cli.app.meta(["models", "ls"])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "Traceback" not in combined
    assert "Error:" in combined
    assert "Set TOGETHER_BASE_URL to https://api.together.ai." in " ".join(combined.split())


def test_whoami_html_error_exits_without_traceback(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from together.lib.cli._track_cli import CliTrackingEvents

    monkeypatch.setenv("TOGETHER_API_KEY", "key")
    monkeypatch.delenv("TOGETHER_BASE_URL", raising=False)
    monkeypatch.setattr(cli, "load_stored_credentials", lambda: None)
    monkeypatch.setattr(cli, "flush_pending_events", lambda: None)

    tracked: list[tuple[object, dict[str, object]]] = []

    def capture_track(event: object, payload: dict[str, object]) -> None:
        tracked.append((event, payload))

    monkeypatch.setattr(cli, "track_cli", capture_track)

    html = "<!DOCTYPE html><html><body><h1>Page not found</h1></body></html>"
    response = httpx.Response(
        404,
        headers={"content-type": "text/html"},
        text=html,
        request=httpx.Request("GET", "https://api.together.ai/v1/v3/whoami"),
    )
    err = NotFoundError(html, response=response, body=html)

    async def boom(_client: object) -> None:
        raise err

    monkeypatch.setattr(cli, "_resolve_project_id", boom)

    with pytest.raises(SystemExit) as exc_info:
        cli.app.meta(["models", "ls"])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "Traceback" not in combined
    assert "unexpected HTML response" in combined
    assert "<!DOCTYPE" not in combined
    assert "Page not found" not in combined

    failure = next(payload for event, payload in tracked if event is CliTrackingEvents.CommandFailed)
    assert failure["error"] == "NotFoundError: Error code: 404 - received unexpected HTML response"
    assert "SystemExit" not in str(failure["error"])
