from __future__ import annotations

import logging
from contextlib import contextmanager

import httpx
import pytest

from together.lib.cli.utils._debug import (
    CliDebugLogFilter,
    mask_secret,
    extract_request_id,
    is_noisy_log_message,
    render_request_lines,
    render_session_lines,
    render_response_lines,
    format_duration_for_display,
)


def test_mask_secret_keeps_only_tail() -> None:
    assert mask_secret("abcdefghijklmnop") == "…mnop"
    assert mask_secret("abcd") == "<redacted>"
    assert mask_secret("") == "<redacted>"


def test_extract_request_id_prefers_x_request_id() -> None:
    headers = httpx.Headers({"cf-ray": "ray-1", "x-request-id": "req_abc"})
    assert extract_request_id(headers) == "req_abc"


def test_noisy_sdk_and_analytics_messages_are_dropped() -> None:
    assert is_noisy_log_message("Request options: {'headers': {'Authorization': 'Bearer x'}}")
    assert is_noisy_log_message('HTTP Response: GET https://api.together.ai/v1/whoami "200 OK" Headers(...)')
    assert is_noisy_log_message("Sending HTTP Request: GET https://api.together.ai/v1/whoami")
    assert is_noisy_log_message("Analytics event sending")
    assert is_noisy_log_message("Updating hash with chunk of size 8192")
    assert is_noisy_log_message("Encountered httpx.HTTPStatusError")
    assert not is_noisy_log_message("Retrying request to /whoami in 1.000000 seconds")
    assert not is_noisy_log_message("Raising timeout error")


def test_log_filter_uses_interpolated_message() -> None:
    log_filter = CliDebugLogFilter()
    noisy = logging.LogRecord(
        "together._base_client",
        logging.DEBUG,
        __file__,
        1,
        "Request options: %s",
        ({"headers": "secret"},),
        None,
    )
    useful = logging.LogRecord(
        "together._base_client",
        logging.INFO,
        __file__,
        1,
        "Retrying request to %s in %f seconds",
        ("/whoami", 1.0),
        None,
    )
    assert log_filter.filter(noisy) is False
    assert log_filter.filter(useful) is True


def test_request_render_is_method_and_path_only() -> None:
    request = httpx.Request(
        "POST",
        "https://api.together.ai/v1/fine-tunes?api_key=secretvalue&foo=bar",
        headers={
            "Authorization": "Bearer supersecretapikeyvalue",
            "Content-Type": "application/json",
            "X-Stainless-Lang": "python",
            "X-Stainless-Retry-Count": "2",
            "Accept-Encoding": "gzip",
        },
        content=b'{"model":"demo"}',
    )
    blob = "\n".join(render_request_lines(request, base_url="https://api.together.ai/v1"))
    assert "→ POST" in blob
    assert "/fine-tunes" in blob
    assert "foo=bar" not in blob
    assert "secretvalue" not in blob
    assert "supersecretapikeyvalue" not in blob
    assert "retry 2" in blob
    assert "authorization" not in blob.lower()
    assert "content-type" not in blob.lower()
    assert "demo" not in blob


def test_response_render_is_status_line_only() -> None:
    request = httpx.Request("GET", "https://api.together.ai/v1/whoami")
    response = httpx.Response(
        200,
        json={"project_id": "proj", "organization_id": "org"},
        headers={
            "x-request-id": "req_test_123",
            "content-type": "application/json",
            "date": "Wed, 01 Jan 2024 00:00:00 GMT",
            "server": "cloudflare",
            "cf-ray": "should-not-duplicate-if-request-id-present",
        },
        request=request,
    )
    blob = "\n".join(render_response_lines(response, elapsed=0.048))
    assert "← 200" in blob
    assert "req_test_123" in blob
    assert format_duration_for_display(0.048) in blob
    assert "project_id" not in blob
    assert "organization_id" not in blob
    assert "cloudflare" not in blob.lower()
    assert "content-type" not in blob.lower()
    assert "cf-ray" not in blob.lower()


def test_session_banner_masks_api_key() -> None:
    blob = "\n".join(
        render_session_lines(
            command="whoami",
            is_beta_command=False,
            base_url="https://api.together.ai/v1/",
            project_id="proj",
            api_key="abcdefghijklmnop",
            timeout=60,
            max_retries=0,
        )
    )
    assert "tg whoami" in blob
    assert "abcdefghijklmnop" not in blob
    assert "…mnop" in blob
    assert "proj" in blob
    assert "retries=0" in blob


async def test_show_loading_status_skips_spinner_when_debug(monkeypatch: pytest.MonkeyPatch) -> None:
    from together.lib.cli.utils import _debug
    from together.lib.cli.utils._console import console
    from together.lib.cli.components.loader import show_loading_status

    monkeypatch.setattr(_debug, "_enabled", True)

    def fail_status(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("spinner should be skipped in debug mode")

    monkeypatch.setattr(console, "status", fail_status)

    async def done() -> str:
        return "ok"

    assert await show_loading_status("Loading widgets...", done()) == "ok"


async def test_show_loading_status_uses_spinner_when_not_debug(monkeypatch: pytest.MonkeyPatch) -> None:
    from together.lib.cli.utils import _debug
    from together.lib.cli.utils._console import console
    from together.lib.cli.components.loader import show_loading_status

    monkeypatch.setattr(_debug, "_enabled", False)
    used = {"status": False}

    @contextmanager
    def fake_status(*_args: object, **_kwargs: object):
        used["status"] = True
        yield

    monkeypatch.setattr(console, "status", fake_status)

    async def done() -> int:
        return 1

    assert await show_loading_status("Loading...", done()) == 1
    assert used["status"] is True
