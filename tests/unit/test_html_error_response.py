"""CLI must not dump HTML error bodies to the user."""

from __future__ import annotations

import httpx
import pytest

from together import InternalServerError, NotFoundError
from together.lib.cli.utils._api_error import (
    report_api_error,
    is_html_api_error,
    html_api_error_message,
)
from together.lib.cli._track_cli import format_cli_error_for_telemetry


def _not_found(*, headers: dict[str, str] | None = None, text: str) -> NotFoundError:
    response = httpx.Response(
        404,
        headers=headers or {},
        text=text,
        request=httpx.Request("GET", "https://api.together.ai/v1/v3/whoami"),
    )
    return NotFoundError(text, response=response, body=text)


def _proxy_html_502(*, body: object) -> InternalServerError:
    """HTML 502 with a lying content-type and non-str SDK body (message has Error code prefix)."""
    html = "<html><body>Bad Gateway</body></html>"
    response = httpx.Response(
        502,
        headers={"content-type": "application/octet-stream"},
        text=html,
        request=httpx.Request("GET", "https://api.together.ai/v1/v3/whoami"),
    )
    return InternalServerError(f"Error code: 502 - {html}", response=response, body=body)


@pytest.mark.parametrize(
    ("headers", "body", "expected"),
    [
        ({"content-type": "text/html; charset=utf-8"}, "anything", True),
        ({"content-type": "application/json"}, '<!DOCTYPE html><html lang="en">', True),
        ({"content-type": "application/json"}, "<html><body>nope</body></html>", True),
        ({"content-type": "application/json"}, '{"error":"not found"}', False),
        ({}, "plain text error", False),
    ],
)
def test_is_html_api_error(headers: dict[str, str], body: str, expected: bool) -> None:
    assert is_html_api_error(_not_found(headers=headers, text=body)) is expected


@pytest.mark.parametrize("body", [{"proxy": True}, None, b"<html><body>Bad Gateway</body></html>"])
def test_is_html_api_error_octet_stream_non_str_body(body: object) -> None:
    err = _proxy_html_502(body=body)
    assert not str(err).lstrip().lower().startswith("<html")
    assert is_html_api_error(err) is True


def test_is_html_api_error_strips_error_code_prefix_when_response_empty() -> None:
    html = "<html><body>Bad Gateway</body></html>"
    response = httpx.Response(
        502,
        headers={"content-type": "application/octet-stream"},
        text="",
        request=httpx.Request("GET", "https://api.together.ai/v1/v3/whoami"),
    )
    err = InternalServerError(f"Error code: 502 - {html}", response=response, body={"proxy": True})
    assert is_html_api_error(err) is True


def test_html_api_error_message_hides_body() -> None:
    html = "<!DOCTYPE html><html><body><h1>Page not found</h1></body></html>"
    err = _not_found(headers={"content-type": "text/html"}, text=html)
    msg = html_api_error_message(err)
    assert msg == "Error code: 404 - received unexpected HTML response"
    assert "Page not found" not in msg


def test_report_api_error_does_not_print_html(capsys: pytest.CaptureFixture[str]) -> None:
    html = "<!DOCTYPE html><html><body><h1>Page not found</h1></body></html>"
    report_api_error(_not_found(headers={"content-type": "text/html"}, text=html), json=False)

    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "unexpected HTML response" in combined
    assert "<!DOCTYPE" not in combined
    assert "Page not found" not in combined


def test_report_api_error_hides_proxy_octet_stream_html(capsys: pytest.CaptureFixture[str]) -> None:
    report_api_error(_proxy_html_502(body={"proxy": True}), json=False)

    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "unexpected HTML response" in combined
    assert "<html" not in combined
    assert "Bad Gateway" not in combined


def test_telemetry_hides_proxy_octet_stream_html() -> None:
    out = format_cli_error_for_telemetry(_proxy_html_502(body={"proxy": True}))
    assert out == "InternalServerError: Error code: 502 - received unexpected HTML response"
    assert "<html" not in out
    assert "Bad Gateway" not in out


def test_report_api_error_json_uses_emit_json(capsys: pytest.CaptureFixture[str]) -> None:
    import json

    from together.lib.cli.utils._json_mode import use_json_mode, json_was_emitted

    use_json_mode(True)
    html = "<!DOCTYPE html><html><body><h1>Page not found</h1></body></html>"
    report_api_error(_not_found(headers={"content-type": "text/html"}, text=html), json=True)

    assert json_was_emitted() is True
    payload = json.loads(capsys.readouterr().out)
    assert payload == {"error": "Error code: 404 - received unexpected HTML response"}
    use_json_mode(False)
