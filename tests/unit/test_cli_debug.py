from __future__ import annotations

import os
import logging
from contextlib import contextmanager

import httpx
import pytest

from together.lib.cli.utils._debug import (
    CliDebugLogFilter,
    mask_secret,
    extract_request_id,
    teardown_cli_debug,
    is_noisy_log_message,
    render_request_lines,
    render_session_lines,
    render_response_lines,
    setup_cli_debug_logging,
    sanitize_debug_log_message,
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


def test_session_banner_missing_key() -> None:
    blob = "\n".join(
        render_session_lines(
            command="whoami",
            is_beta_command=False,
            base_url="https://api.together.ai/v1/",
            project_id=None,
            api_key=None,
            timeout=None,
            max_retries=0,
        )
    )
    assert "key=<missing>" in blob
    assert "project=<unresolved>" in blob


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
    assert "[muted]debug[/muted]" not in blob


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


def test_sanitize_debug_log_strips_presigned_query() -> None:
    url = (
        "https://s3.amazonaws.com/bucket/key?X-Amz-Algorithm=AWS4-HMAC-SHA256"
        "&X-Amz-Credential=AKIAEXAMPLE%2F20260101%2Fus-east-1%2Fs3%2Faws4_request"
        "&X-Amz-Signature=deadbeefcafebabe"
    )
    out = sanitize_debug_log_message(f"Upload redirected to {url}")
    assert out.startswith("Upload redirected to https://s3.amazonaws.com/bucket/key")
    assert "X-Amz-" not in out
    assert "AKIAEXAMPLE" not in out
    assert "deadbeef" not in out
    assert "?" not in out


def test_teardown_restores_together_log_env_and_logger_level(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("TOGETHER_LOG", raising=False)
    together_logger = logging.getLogger("together")
    previous_level = together_logger.level
    together_logger.setLevel(logging.WARNING)
    try:
        setup_cli_debug_logging()
        assert os.environ.get("TOGETHER_LOG") == "debug"
        assert together_logger.level == logging.DEBUG
        teardown_cli_debug()
        assert "TOGETHER_LOG" not in os.environ
        assert together_logger.level == logging.WARNING

        from together.lib.utils._log import log_debug

        log_debug("Analytics event sending", body="should-not-print")
        captured = capsys.readouterr()
        assert "Analytics event sending" not in captured.err
        assert "should-not-print" not in captured.err
    finally:
        teardown_cli_debug()
        together_logger.setLevel(previous_level)


def test_log_warn_not_duplicated_under_cli_debug(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("TOGETHER_LOG", raising=False)
    setup_cli_debug_logging()
    try:
        from together.lib.utils._log import log_warn, log_warn_once

        log_warn("validation loops disabled")
        log_warn_once("cli-debug-warn-once-unique")
        err = capsys.readouterr().err
        assert err.count("validation loops disabled") == 1
        assert err.count("cli-debug-warn-once-unique") == 1
        assert "message=" in err
    finally:
        teardown_cli_debug()


def test_cli_debug_handler_prints_traceback(capsys: pytest.CaptureFixture[str]) -> None:
    setup_cli_debug_logging()
    try:
        logger = logging.getLogger("together._base_client")
        try:
            raise TimeoutError("connect timed out")
        except TimeoutError:
            logger.debug("Encountered httpx.TimeoutException", exc_info=True)
        err = capsys.readouterr().err
        assert "Encountered httpx.TimeoutException" in err
        assert "TimeoutError" in err
        assert "connect timed out" in err
        assert "Traceback" in err
    finally:
        teardown_cli_debug()
