from __future__ import annotations

import os
import re
import json
import time
import logging
import platform
from typing import Union, Mapping
from collections.abc import Sequence
from typing_extensions import override

import httpx
from rich.markup import escape as escape_rich_markup

from together import __version__
from together.lib.utils._log import set_cli_debug_console_redirect
from together.lib.cli._track_cli import _redact_secrets_in_error_text
from together.lib.cli.utils._console import error_console

_START_EXTENSION = "together_cli_debug_start"

MAX_BODY_READ = 64 * 1024
MAX_BODY_DISPLAY = 8 * 1024

_SECRET_HEADER_NAMES = {
    "authorization",
    "proxy-authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "api-key",
    "x-auth-token",
}

_SECRET_QUERY_KEYS = {
    "access_token",
    "id_token",
    "refresh_token",
    "api_key",
    "apikey",
    "password",
    "passwd",
    "client_secret",
    "token",
    "secret",
    "credentials",
    "key",
}

_REQUEST_ID_HEADERS = (
    "x-request-id",
    "x-together-request-id",
    "cf-ray",
    "x-amzn-requestid",
    "x-amzn-trace-id",
    "traceparent",
    "x-cloud-trace-context",
)

_SKIP_REQUEST_HEADERS = {
    "accept",
    "accept-encoding",
    "connection",
    "content-length",
    "host",
}

_SKIP_RESPONSE_HEADERS = {
    "accept-ranges",
    "age",
    "alt-svc",
    "cache-control",
    "cf-cache-status",
    "connection",
    "content-encoding",
    "content-security-policy",
    "date",
    "expires",
    "keep-alive",
    "nel",
    "pragma",
    "priority",
    "referrer-policy",
    "report-to",
    "server",
    "set-cookie",
    "strict-transport-security",
    "transfer-encoding",
    "vary",
    "via",
    "x-content-type-options",
    "x-frame-options",
    "x-xss-protection",
}

_STREAM_CONTENT_TYPES = {
    "text/event-stream",
    "application/octet-stream",
    "application/grpc",
}

_NOISY_LOG_PATTERNS = (
    re.compile(r"^Request options:"),
    re.compile(r"^Sending HTTP Request:"),
    re.compile(r"^HTTP Response:"),
    re.compile(r"^HTTP Request:"),
    re.compile(r"Analytics event sending"),
    re.compile(r"Analytics tracking disabled"),
    re.compile(r"Error tracking api request"),
    re.compile(r"Updating hash with chunk"),
    re.compile(r"^Starting file checksum"),
    re.compile(r"^hash complete", re.I),
    re.compile(r"^1 retry left$"),
    re.compile(r"^\d+ retries left$"),
    re.compile(r"^Not retrying$"),
    re.compile(r"^Retrying as header"),
    re.compile(r"^Not retrying as header"),
    re.compile(r"^Retrying due to status code"),
    re.compile(r"^Could not read JSON from response"),
    re.compile(r"^Encountered httpx\.HTTPStatusError"),
    re.compile(r"^Re-raising status error$"),
)

_enabled = False
_base_url = ""
_saved_httpx_level: int | None = None
_saved_together_propagate: bool | None = None


def is_enabled() -> bool:
    return _enabled


def mask_secret(value: str, *, visible: int = 4) -> str:
    if not value:
        return "<redacted>"
    if len(value) <= visible:
        return "<redacted>"
    return f"…{value[-visible:]}"


def is_secret_header(name: str) -> bool:
    lowered = name.lower()
    if lowered in _SECRET_HEADER_NAMES:
        return True
    if "api-key" in lowered or "api_key" in lowered:
        return True
    if "secret" in lowered or "password" in lowered:
        return True
    if lowered.endswith("token") or lowered.endswith("-token"):
        return True
    return False


def redact_header_value(name: str, value: str) -> str:
    if not is_secret_header(name):
        return value
    if name.lower() == "authorization":
        kind, _, rest = value.partition(" ")
        if rest and kind.lower() in {"bearer", "basic", "token"}:
            return f"{kind} {mask_secret(rest)}"
    return "<redacted>"


def extract_request_id(headers: Mapping[str, str] | httpx.Headers) -> str | None:
    lowered = {str(key).lower(): str(value) for key, value in headers.items()}
    for name in _REQUEST_ID_HEADERS:
        value = lowered.get(name)
        if value:
            return value
    for key, value in lowered.items():
        if "request-id" in key or key.endswith("-trace-id"):
            return value
    return None


def is_noisy_log_message(message: str) -> bool:
    text = message.strip()
    return any(pattern.search(text) for pattern in _NOISY_LOG_PATTERNS)


def _content_type(headers: Mapping[str, str] | httpx.Headers) -> str:
    raw = headers.get("content-type") if hasattr(headers, "get") else None
    if not raw:
        return ""
    return str(raw).split(";", 1)[0].strip().lower()


def _should_skip_body(content_type: str) -> bool:
    if content_type in _STREAM_CONTENT_TYPES:
        return True
    return content_type.startswith(("image/", "audio/", "video/"))


def preview_body(content: bytes, content_type: str, *, max_display: int = MAX_BODY_DISPLAY) -> str | None:
    if not content:
        return None
    if content_type.startswith("multipart/"):
        return f"<multipart {len(content)} bytes>"
    if _should_skip_body(content_type):
        return f"<{content_type or 'binary'} {len(content)} bytes>"

    text: str
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return f"<binary {len(content)} bytes>"

    stripped = text.strip()
    if content_type in {"application/json", "application/problem+json"} or stripped[:1] in "{[":
        try:
            parsed: object = json.loads(stripped)
        except ValueError:
            parsed = None
        if parsed is not None:
            text = json.dumps(parsed, indent=2, ensure_ascii=False, default=str)

    text = _redact_secrets_in_error_text(text)
    if len(text) > max_display:
        return f"{text[:max_display]}\n… truncated ({len(content)} bytes total)"
    return text


def _skip_header(name: str, *, kind: str, request_id: str | None) -> bool:
    lowered = name.lower()
    if lowered.startswith("x-stainless-"):
        return True
    if kind == "request" and lowered in _SKIP_REQUEST_HEADERS:
        return True
    if kind == "response" and lowered in _SKIP_RESPONSE_HEADERS:
        return True
    if request_id is not None and lowered in _REQUEST_ID_HEADERS:
        return True
    if request_id is not None and ("request-id" in lowered or lowered.endswith("-trace-id")):
        return True
    return False


def interesting_headers(
    headers: Mapping[str, str] | httpx.Headers,
    *,
    kind: str,
    request_id: str | None = None,
) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for name, value in headers.items():
        if _skip_header(str(name), kind=kind, request_id=request_id):
            continue
        items.append((str(name), redact_header_value(str(name), str(value))))
    items.sort(key=lambda item: item[0].lower())
    return items


def _safe_url(url: httpx.URL, *, base_url: str = "") -> str:
    query_items = list(url.params.multi_items()) if url.query else []
    if query_items:
        redacted = [
            (
                key,
                "<redacted>"
                if key.lower() in _SECRET_QUERY_KEYS or "token" in key.lower() or "secret" in key.lower()
                else value,
            )
            for key, value in query_items
        ]
        url = url.copy_with(params=redacted)

    rendered = str(url)
    base = base_url.rstrip("/")
    if base and rendered.startswith(base):
        rest = rendered[len(base) :]
        return rest if rest.startswith("/") else f"/{rest}"
    return rendered


def _format_duration(seconds: float) -> str:
    ms = seconds * 1000
    if ms < 10:
        return f"{ms:.1f}ms"
    if ms < 1000:
        return f"{ms:.0f}ms"
    return f"{seconds:.2f}s"


def _format_timeout(timeout: float | httpx.Timeout | None) -> str:
    if timeout is None:
        return "off"
    if isinstance(timeout, (int, float)):
        return f"{timeout:g}s"
    read = timeout.read
    if read is None:
        return "off"
    return f"{read:g}s"


def _status_style(status_code: int) -> str:
    if status_code < 300:
        return "success"
    if status_code < 400:
        return "info"
    if status_code < 500:
        return "warning"
    return "error"


def _read_request_body(request: httpx.Request) -> bytes | None:
    try:
        return request.content
    except httpx.RequestNotRead:
        return None
    except Exception:
        return None


def _content_length_ok_for_peek(response: httpx.Response) -> bool:
    if _should_skip_body(_content_type(response.headers)):
        return False
    accept = response.request.headers.get("accept", "")
    if accept.startswith("text/event-stream"):
        return False
    length_header = response.headers.get("content-length")
    if length_header is None:
        return False
    try:
        length = int(length_header)
    except ValueError:
        return False
    return 0 < length <= MAX_BODY_READ


def _peek_response_body(response: httpx.Response) -> bytes | None:
    if hasattr(response, "_content"):
        return bytes(response.content)
    return None


def render_session_lines(
    *,
    command: str,
    is_beta_command: bool,
    base_url: str,
    project_id: str | None,
    api_key: str | None,
    timeout: float | httpx.Timeout | None,
    max_retries: int,
) -> list[str]:
    path = command.strip()
    if is_beta_command and path:
        path = f"beta {path}"
    elif is_beta_command:
        path = "beta"
    invocation = f"tg {path}".rstrip()

    key_display = mask_secret(api_key) if api_key else "<missing>"
    project_display = project_id or "<unresolved>"
    runtime = f"python {platform.python_version()}  {platform.system().lower()}"

    return [
        f"[muted]debug[/muted]  [primary]tg {escape_rich_markup(__version__)}[/primary]  [dim]{escape_rich_markup(runtime)}[/dim]",
        f"[muted]debug[/muted]  [bold]{escape_rich_markup(invocation)}[/bold]",
        f"[muted]debug[/muted]  [dim]{escape_rich_markup(base_url)}[/dim]",
        (
            f"[muted]debug[/muted]  project={escape_rich_markup(project_display)}  "
            f"key={escape_rich_markup(key_display)}  "
            f"timeout={escape_rich_markup(_format_timeout(timeout))}  "
            f"retries={max_retries}"
        ),
    ]


def render_request_lines(request: httpx.Request, *, base_url: str = "") -> list[str]:
    method = request.method.upper()
    url = _safe_url(request.url, base_url=base_url)
    retry = request.headers.get("x-stainless-retry-count")
    retry_bit = ""
    if retry and retry != "0":
        retry_bit = f"  [warning]retry {escape_rich_markup(retry)}[/warning]"

    lines = [f"[info]→ {escape_rich_markup(method)}[/info] [bold]{escape_rich_markup(url)}[/bold]{retry_bit}"]
    for name, value in interesting_headers(request.headers, kind="request"):
        lines.append(f"  [dim]{escape_rich_markup(name.lower())}:[/dim] {escape_rich_markup(value)}")

    body = preview_body(_read_request_body(request) or b"", _content_type(request.headers))
    if body:
        for line in body.splitlines():
            lines.append(f"  {escape_rich_markup(line)}")
    return lines


def render_response_lines(response: httpx.Response, *, elapsed: float | None = None) -> list[str]:
    status = f"{response.status_code} {response.reason_phrase}".strip()
    style = _status_style(response.status_code)
    extras: list[str] = []
    if elapsed is not None:
        extras.append(f"[dim]{_format_duration(elapsed)}[/dim]")
    request_id = extract_request_id(response.headers)
    if request_id:
        extras.append(f"[muted]{escape_rich_markup(request_id)}[/muted]")

    suffix = ("  " + "  ".join(extras)) if extras else ""
    lines = [f"[{style}]← {escape_rich_markup(status)}[/{style}]{suffix}"]

    for name, value in interesting_headers(response.headers, kind="response", request_id=request_id):
        lines.append(f"  [dim]{escape_rich_markup(name.lower())}:[/dim] {escape_rich_markup(value)}")

    raw = _peek_response_body(response)
    if raw is not None:
        body = preview_body(raw, _content_type(response.headers))
        if body:
            for line in body.splitlines():
                lines.append(f"  {escape_rich_markup(line)}")
    elif _should_skip_body(_content_type(response.headers)):
        content_type = _content_type(response.headers) or "stream"
        length = response.headers.get("content-length")
        size = f"{length} bytes" if length else "stream"
        lines.append(f"  [dim]<{escape_rich_markup(content_type)} {escape_rich_markup(size)}>[/dim]")
    return lines


def _print_lines(lines: Sequence[str]) -> None:
    for line in lines:
        error_console.print(line)


def log_debug_session(
    *,
    command: str,
    is_beta_command: bool,
    base_url: str,
    project_id: str | None,
    api_key: str | None,
    timeout: float | httpx.Timeout | None,
    max_retries: int,
) -> None:
    global _base_url
    _base_url = str(base_url)
    _print_lines(
        render_session_lines(
            command=command,
            is_beta_command=is_beta_command,
            base_url=str(base_url),
            project_id=project_id,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )
    )


def log_debug_note(message: str) -> None:
    error_console.print(f"[muted]debug[/muted]  {escape_rich_markup(message)}")


async def _on_request(request: httpx.Request) -> None:
    if not _enabled:
        return
    request.extensions[_START_EXTENSION] = time.perf_counter()
    _print_lines(render_request_lines(request, base_url=_base_url))


async def _on_response(response: httpx.Response) -> None:
    if not _enabled:
        return
    if not hasattr(response, "_content") and _content_length_ok_for_peek(response):
        try:
            await response.aread()
        except Exception:
            pass
    start = response.request.extensions.get(_START_EXTENSION)
    elapsed: float | None
    if isinstance(start, (int, float)):
        elapsed = time.perf_counter() - float(start)
    else:
        elapsed = None
    _print_lines(render_response_lines(response, elapsed=elapsed))
    error_console.print("")


class CliDebugLogFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            return not is_noisy_log_message(record.getMessage())
        except Exception:
            return True


class CliDebugLogHandler(logging.Handler):
    @override
    def emit(self, record: logging.LogRecord) -> None:
        if not _enabled:
            return
        try:
            message = _redact_secrets_in_error_text(record.getMessage())
            level = record.levelname.lower()
            style = {
                "debug": "muted",
                "info": "info",
                "warning": "warning",
                "error": "error",
                "critical": "error",
            }.get(level, "muted")
            name = record.name.removeprefix("together.").removeprefix("together")
            error_console.print(
                f"[muted]log[/muted]  [{style}]{escape_rich_markup(level)}[/{style}] "
                f"[dim]{escape_rich_markup(name)}[/dim] {escape_rich_markup(message)}"
            )
        except Exception:
            self.handleError(record)


def install_http_debug_hooks(http_client: httpx.AsyncClient | httpx.Client) -> None:
    hooks = http_client.event_hooks
    request_hooks = hooks.setdefault("request", [])
    response_hooks = hooks.setdefault("response", [])
    if _on_request not in request_hooks:
        request_hooks.append(_on_request)
    if _on_response not in response_hooks:
        response_hooks.append(_on_response)


def setup_cli_debug_logging() -> None:
    global _enabled, _saved_httpx_level, _saved_together_propagate
    os.environ.setdefault("TOGETHER_LOG", "debug")
    _enabled = True
    set_cli_debug_console_redirect(True)

    httpx_logger = logging.getLogger("httpx")
    together_logger = logging.getLogger("together")
    _saved_httpx_level = httpx_logger.level
    _saved_together_propagate = together_logger.propagate

    httpx_logger.setLevel(logging.WARNING)
    together_logger.setLevel(logging.DEBUG)
    together_logger.propagate = False

    if not any(isinstance(handler, CliDebugLogHandler) for handler in together_logger.handlers):
        handler = CliDebugLogHandler()
        handler.setLevel(logging.DEBUG)
        handler.addFilter(CliDebugLogFilter())
        together_logger.addHandler(handler)


def teardown_cli_debug() -> None:
    global _enabled, _base_url, _saved_httpx_level, _saved_together_propagate
    _enabled = False
    _base_url = ""
    set_cli_debug_console_redirect(False)

    together_logger = logging.getLogger("together")
    together_logger.handlers = [
        handler for handler in together_logger.handlers if not isinstance(handler, CliDebugLogHandler)
    ]
    if _saved_together_propagate is not None:
        together_logger.propagate = _saved_together_propagate
        _saved_together_propagate = None

    if _saved_httpx_level is not None:
        logging.getLogger("httpx").setLevel(_saved_httpx_level)
        _saved_httpx_level = None


def format_timeout_for_display(timeout: Union[float, httpx.Timeout, None]) -> str:
    return _format_timeout(timeout)


def format_duration_for_display(seconds: float) -> str:
    return _format_duration(seconds)
