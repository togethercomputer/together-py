from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel
from rich.markup import escape as escape_rich_markup

from together import APIError
from together._exceptions import APIStatusError
from together.lib.cli.utils._console import console
from together.lib.cli.utils._json_mode import emit_json


class _ErrorContents(BaseModel):
    message: str
    type: str
    param: Optional[str] = None
    code: Optional[str] = None


class _ErrorEnvelope(BaseModel):
    error: _ErrorContents


class _RPCError(BaseModel):
    message: str
    code: int
    details: Optional[list[Any]] = None


def _parse_error_envelope(body: object) -> _ErrorEnvelope:
    # Pydantic v1: parse_obj; v2: model_validate
    if hasattr(_ErrorEnvelope, "model_validate"):
        return _ErrorEnvelope.model_validate(body)
    return _ErrorEnvelope.parse_obj(body)  # type: ignore


def _parse_rpc_error_envelope(body: object) -> _RPCError:
    # Pydantic v1: parse_obj; v2: model_validate
    if hasattr(_RPCError, "model_validate"):
        return _RPCError.model_validate(body)
    return _RPCError.parse_obj(body)  # type: ignore


def _looks_like_html(text: str) -> bool:
    """True for HTML (or XHTML) payloads, including common leading noise.

    Proxies often prefix pages with a BOM, ``<!-- nginx -->`` comments, or
    ``<?xml ...?>`` / bare ``<head>`` before ``<!DOCTYPE html>`` / ``<html>``.
    """
    s = text.lstrip("\ufeff").lstrip().lower()
    while s.startswith("<!--"):
        end = s.find("-->")
        if end < 0:
            # Truncated comment is still HTML-shaped enough to hide.
            return True
        s = s[end + 3 :].lstrip("\ufeff").lstrip()
    return s.startswith("<!doctype html") or s.startswith("<html") or s.startswith("<?xml") or s.startswith("<head")


def _error_text_without_status_prefix(e: APIError) -> str:
    """Strip Stainless's ``Error code: N - `` prefix so HTML sniffing can see the body."""
    text = e.message
    if isinstance(e, APIStatusError):
        prefix = f"Error code: {e.status_code} - "
        if text.startswith(prefix):
            return text[len(prefix) :]
    return text


def is_html_api_error(e: APIError) -> bool:
    """True when the API returned an HTML page instead of a JSON error envelope.

    Content-type is unreliable (proxies often send ``application/octet-stream``).
    ``e.body`` may be non-str after JSON parsing, and ``str(e)`` is often
    ``Error code: N - ...``, so sniff the raw response text and the unprefixed message.
    """
    if isinstance(e, APIStatusError):
        content_type = e.response.headers.get("content-type", "").lower()
        if "text/html" in content_type:
            return True
        try:
            if _looks_like_html(e.response.text):
                return True
        except Exception:
            pass
    if isinstance(e.body, (bytes, bytearray)):
        try:
            if _looks_like_html(e.body.decode("utf-8", errors="ignore")):
                return True
        except Exception:
            pass
    elif isinstance(e.body, str) and _looks_like_html(e.body):
        return True
    return _looks_like_html(_error_text_without_status_prefix(e))


def html_api_error_message(e: APIError) -> str:
    status = e.status_code if isinstance(e, APIStatusError) else None
    if status is not None:
        return f"Error code: {status} - received unexpected HTML response"
    return "received unexpected HTML response"


def parse_api_error(e: APIError) -> tuple[str, dict[str, Any]]:
    # If the error is from the API and uses the standard error envelope, print the message
    message = ""
    dump = {}
    try:
        standard_envelope = _parse_error_envelope(e.body)
        dump = standard_envelope.model_dump()
        message = standard_envelope.error.message
    # Some APIs are returning the RPC error format, so we need to parse that instead.
    except Exception:
        rpc_envelope = _parse_rpc_error_envelope(e.body)
        dump = rpc_envelope.model_dump()
        if isinstance(rpc_envelope.details, list):
            for detail_dict in rpc_envelope.details:
                message = detail_dict["detail"]
        else:
            message = rpc_envelope.message

    return message, dump


def _emit_error_message(error_msg: str, *, json: bool) -> None:
    """Same ``{"error": ...}`` / ``Error:`` shape as launcher helpers like ``_print_missing_api_key``."""
    if json:
        emit_json({"error": error_msg})
        return
    console.print(f"[red]Error:[/red] {escape_rich_markup(error_msg)}")


def try_handle_server_error_message(e: APIError, json: bool) -> None:
    message, dump = parse_api_error(e)

    if json:
        emit_json(dump)
        return
    console.print(f"[red]×[/red] [bold]Error[/bold]")
    console.print(f"  [white]{escape_rich_markup(message)}[/white]")


def report_api_error(e: APIError, *, json: bool) -> None:
    """Print an API error for the CLI without re-raising (no stack trace)."""
    if is_html_api_error(e):
        _emit_error_message(html_api_error_message(e), json=json)
        return

    try:
        try_handle_server_error_message(e, json)
    except Exception:
        if e.body is not None:
            error_msg = getattr(e.body, "message", str(e.body))
        else:
            error_msg = str(e)
        _emit_error_message(str(error_msg), json=json)
