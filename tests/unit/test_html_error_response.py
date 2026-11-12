"""CLI must not dump HTML error bodies to the user."""

from __future__ import annotations

import httpx
import pytest

from together import NotFoundError
from together.lib.cli.utils._api_error import (
    html_api_error_message,
    is_html_api_error,
    report_api_error,
)


def _not_found(*, headers: dict[str, str] | None = None, text: str) -> NotFoundError:
    response = httpx.Response(
        404,
        headers=headers or {},
        text=text,
        request=httpx.Request("GET", "https://api.together.ai/v1/v3/whoami"),
    )
    return NotFoundError(text, response=response, body=text)


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
