"""CLI base URLs that still end in the legacy `/v1` resolve to the API root."""

from __future__ import annotations

from typing import Optional

import pytest

import together.lib.cli as cli


@pytest.mark.parametrize(
    ("env_url", "flag_url", "want"),
    [
        ("https://staging.together.ai/v1/", None, "https://staging.together.ai"),
        (None, "https://api.together.ai/v1", "https://api.together.ai"),
        ("http://127.0.0.1:4010", None, "http://127.0.0.1:4010"),
    ],
)
def test_create_client_trims_legacy_v1_base_url(
    monkeypatch: pytest.MonkeyPatch, env_url: Optional[str], flag_url: Optional[str], want: str
) -> None:
    monkeypatch.setenv("TOGETHER_API_KEY", "key")
    monkeypatch.delenv("TOGETHER_BASE_URL", raising=False)
    if env_url is not None:
        monkeypatch.setenv("TOGETHER_BASE_URL", env_url)

    client, _ = cli._create_client(api_key=None, base_url=flag_url, timeout=None, max_retries=None, project_id=None)

    assert str(client.base_url).rstrip("/") == want
