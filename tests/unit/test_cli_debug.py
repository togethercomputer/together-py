from __future__ import annotations

import logging

import httpx

from together.lib.cli.utils._debug import (
    CliDebugLogFilter,
    mask_secret,
    preview_body,
    extract_request_id,
    redact_header_value,
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


def test_redact_bearer_authorization() -> None:
    out = redact_header_value("Authorization", "Bearer supersecretapikeyvalue")
    assert "supersecret" not in out
    assert out.startswith("Bearer ")
    assert out.endswith("alue")


def test_redact_cookie_entirely() -> None:
    assert redact_header_value("Cookie", "session=abc") == "<redacted>"


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


def test_preview_body_pretty_prints_json_and_redacts() -> None:
    raw = b'{"token":"sk-abcdefghijklmnopqrstuvwxyz0123456789","ok":true}'
    out = preview_body(raw, "application/json")
    assert out is not None
    assert "ok" in out
    assert "sk-abcdefghijklmnopqrstuvwxyz0123456789" not in out


def test_preview_body_truncates() -> None:
    out = preview_body(b"x" * 5000, "text/plain", max_display=50)
    assert out is not None
    assert "truncated" in out
    assert len(out) < 5000


def test_preview_body_skips_multipart() -> None:
    assert preview_body(b"form-data", "multipart/form-data") == "<multipart 9 bytes>"


def test_request_render_hides_stainless_and_secrets() -> None:
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
    blob = "\n".join(render_request_lines(request))
    assert "→ POST" in blob
    assert "supersecretapikeyvalue" not in blob
    assert "secretvalue" not in blob
    assert "foo=bar" in blob
    assert "retry 2" in blob
    assert "x-stainless-lang" not in blob.lower()
    assert "accept-encoding" not in blob.lower()
    assert '"model": "demo"' in blob


def test_response_render_keeps_useful_fields_and_drops_noise() -> None:
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
    assert "project_id" in blob
    assert "server:" not in blob.lower()
    assert "date:" not in blob.lower()


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
