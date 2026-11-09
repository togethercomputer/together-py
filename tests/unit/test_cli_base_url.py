"""CLI base URLs that still end in the legacy `/v1` print a warning naming the root to use."""

from __future__ import annotations

from typing import Optional

import pytest

import together.lib.cli as cli


@pytest.mark.parametrize(
    ("env_url", "flag_url", "source", "root"),
    [
        ("https://staging.together.ai/v1/", None, "TOGETHER_BASE_URL", "https://staging.together.ai"),
        (None, "https://api.together.ai/v1", "--base-url", "https://api.together.ai"),
    ],
)
def test_create_client_warns_on_legacy_v1_base_url(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    env_url: Optional[str],
    flag_url: Optional[str],
    source: str,
    root: str,
) -> None:
    monkeypatch.setenv("TOGETHER_API_KEY", "key")
    monkeypatch.delenv("TOGETHER_BASE_URL", raising=False)
    if env_url is not None:
        monkeypatch.setenv("TOGETHER_BASE_URL", env_url)

    client, _ = cli._create_client(api_key=None, base_url=flag_url, timeout=None, max_retries=None, project_id=None)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert f"Set {source} to {root}." in " ".join(captured.err.split())
    assert str(client.base_url).rstrip("/") == f"{root}/v1"


def test_create_client_does_not_warn_on_api_root(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("TOGETHER_API_KEY", "key")
    monkeypatch.setenv("TOGETHER_BASE_URL", "http://127.0.0.1:4010")

    cli._create_client(api_key=None, base_url=None, timeout=None, max_retries=None, project_id=None)

    assert capsys.readouterr().err == ""
