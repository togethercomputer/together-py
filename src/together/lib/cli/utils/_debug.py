from __future__ import annotations

import os
import re
import json
import time
import logging
import platform
import tempfile
import threading
import traceback
from typing import IO, Union, Mapping, AsyncIterator
from datetime import datetime
from collections.abc import Sequence
from typing_extensions import override

import httpx
from rich.text import Text
from rich.markup import escape as escape_rich_markup

from together import __version__
from together.lib.utils._log import set_cli_debug_console_redirect
from together.lib.cli._track_cli import _redact_secrets_in_error_text
from together.lib.cli.utils._console import error_console

_START_EXTENSION = "together_cli_debug_start"

_REQUEST_ID_HEADERS = (
    "x-request-id",
    "x-together-request-id",
    "cf-ray",
    "x-amzn-requestid",
    "x-amzn-trace-id",
    "traceparent",
    "x-cloud-trace-context",
)

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

# Bodies larger than this are truncated in the debug log file.
_MAX_LOGGED_BODY_BYTES = 1024 * 1024

_SENSITIVE_HEADERS = frozenset(
    {
        "authorization",
        "proxy-authorization",
        "cookie",
        "set-cookie",
        "x-api-key",
        "api-key",
        "x-amz-security-token",
    }
)

# Presigned-URL signing params (S3, GCS, Azure SAS, CloudFront). Values are
# short-lived credentials, so redact them even in the on-disk log.
_SIGNED_URL_PARAM_RE = re.compile(
    r"(?i)([?&])(x-amz-(?:signature|credential|security-token)|x-goog-(?:signature|credential)|"
    r"sig|signature|policy|key-pair-id)=([^&#\s\"']+)"
)

_TEXT_CONTENT_TYPE_RE = re.compile(
    r"(?i)^(text/|application/(?:[\w.+-]*\+)?(?:json|xml|x-ndjson|x-www-form-urlencoded))"
)

_enabled = False
_base_url = ""
_log_file: IO[str] | None = None
_log_file_path: str | None = None
_log_lock = threading.Lock()
_saved_httpx_level: int | None = None
_saved_together_level: int | None = None
_saved_together_propagate: bool | None = None
# (was_set, value) for TOGETHER_LOG before setup; None means setup did not snapshot yet.
_saved_together_log_env: tuple[bool, str] | None = None


def is_enabled() -> bool:
    return _enabled


def debug_log_path() -> str | None:
    return _log_file_path


def mask_secret(value: str, *, visible: int = 4) -> str:
    if not value:
        return "<redacted>"
    if len(value) <= visible:
        return "<redacted>"
    return f"…{value[-visible:]}"


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


_URL_WITH_QUERY_RE = re.compile(r"(https?://[^\s?#]+)(\?[^\s]*)", re.IGNORECASE)


def sanitize_debug_log_message(message: str) -> str:
    """Redact secrets and drop URL query strings (presigned S3, SigV4, tokens)."""
    stripped = _URL_WITH_QUERY_RE.sub(r"\1", message)
    return _redact_secrets_in_error_text(stripped)


def redact_for_log_file(text: str) -> str:
    """Redact secrets but keep URL query strings (minus presigned signing params)."""
    return _redact_secrets_in_error_text(_SIGNED_URL_PARAM_RE.sub(r"\1\2=<redacted>", text))


def _safe_url(url: httpx.URL, *, base_url: str = "") -> str:
    if url.query:
        url = url.copy_with(query=None)
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
        f"[primary]tg {escape_rich_markup(__version__)}[/primary]  [dim]{escape_rich_markup(runtime)}[/dim]",
        f"[bold]{escape_rich_markup(invocation)}[/bold]",
        f"[dim]{escape_rich_markup(base_url)}[/dim]",
        (
            f"project={escape_rich_markup(project_display)}  "
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

    return [f"[info]→ {escape_rich_markup(method)}[/info] [bold]{escape_rich_markup(url)}[/bold]{retry_bit}"]


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
    return [f"[{style}]← {escape_rich_markup(status)}[/{style}]{suffix}"]


def _write_log_file(text: str) -> None:
    if _log_file is None:
        return
    with _log_lock:
        try:
            _log_file.write(text if text.endswith("\n") else f"{text}\n")
            _log_file.flush()
        except (OSError, ValueError):
            pass


def _debug_print(markup: str = "") -> None:
    # stderr-to-file is not a TTY, so Rich would otherwise wrap at 80 columns
    # and split paths / traceback lines mid-token.
    error_console.print(markup, soft_wrap=True)
    _write_log_file(Text.from_markup(markup).plain)


def _open_log_file() -> None:
    global _log_file, _log_file_path
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    try:
        # mkstemp creates the file with 0600 permissions.
        fd, path = tempfile.mkstemp(prefix=f"tg-debug-{stamp}-", suffix=".log")
        _log_file = os.fdopen(fd, "w", encoding="utf-8", errors="replace")
        _log_file_path = path
    except OSError as e:
        _log_file = None
        _log_file_path = None
        error_console.print(
            f"[muted]debug[/muted] [warning]could not create debug log file: {escape_rich_markup(str(e))}[/warning]",
            soft_wrap=True,
        )


def _close_log_file() -> None:
    global _log_file, _log_file_path
    if _log_file is not None:
        with _log_lock:
            try:
                _log_file.close()
            except OSError:
                pass
        _log_file = None
    _log_file_path = None


def _format_headers(headers: httpx.Headers) -> list[str]:
    lines: list[str] = []
    for key, value in headers.multi_items():
        shown = "<redacted>" if key.lower() in _SENSITIVE_HEADERS else redact_for_log_file(value)
        lines.append(f"    {key}: {shown}")
    return lines


def _is_text_content_type(content_type: str | None) -> bool:
    return bool(content_type) and bool(_TEXT_CONTENT_TYPE_RE.match(content_type or ""))


def _format_body(content: bytes, *, content_type: str | None, truncated: bool = False) -> list[str]:
    if not content:
        return ["    <empty>"]
    if not _is_text_content_type(content_type):
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            return [f"    <{len(content)} bytes of {content_type or 'binary'} data omitted>"]
    else:
        text = content.decode("utf-8", errors="replace")

    if not truncated and "json" in (content_type or "").lower():
        try:
            text = json.dumps(json.loads(text), indent=2, ensure_ascii=False)
        except ValueError:
            pass

    lines = [f"    {line}" for line in redact_for_log_file(text).splitlines()]
    if truncated:
        lines.append(f"    <truncated after {_MAX_LOGGED_BODY_BYTES} bytes>")
    return lines


def _request_label(request: httpx.Request) -> str:
    return f"{request.method.upper()} {redact_for_log_file(str(request.url))}"


def _log_request_details(request: httpx.Request) -> None:
    if _log_file is None:
        return
    lines = [f"  request {_request_label(request)}", "  request headers:", *_format_headers(request.headers)]
    try:
        content = request.content
    except httpx.RequestNotRead:
        lines += ["  request body:", "    <streaming body not captured>"]
    else:
        if content:
            lines += ["  request body:", *_format_body(content, content_type=request.headers.get("content-type"))]
    _write_log_file("\n".join(lines))


class _TeeResponseStream(httpx.AsyncByteStream):
    """Pass response bytes through untouched and log the body once the stream closes.

    Buffering in the response hook would break streaming responses (SSE, log
    follow, file downloads), so we capture raw bytes as the caller reads them.
    """

    def __init__(self, response: httpx.Response, inner: httpx.AsyncByteStream) -> None:
        self._response = response
        self._inner = inner
        self._chunks: list[bytes] = []
        self._captured = 0
        self._total = 0
        self._logged = False

    @override
    async def __aiter__(self) -> AsyncIterator[bytes]:
        async for chunk in self._inner:
            self._total += len(chunk)
            if self._captured < _MAX_LOGGED_BODY_BYTES:
                piece = chunk[: _MAX_LOGGED_BODY_BYTES - self._captured]
                self._chunks.append(piece)
                self._captured += len(piece)
            yield chunk

    @override
    async def aclose(self) -> None:
        try:
            await self._inner.aclose()
        finally:
            self._log_body()

    def _log_body(self) -> None:
        if self._logged:
            return
        self._logged = True
        raw = b"".join(self._chunks)
        truncated = self._total > self._captured
        headers = self._response.headers
        content = raw
        if raw and headers.get("content-encoding") and not truncated:
            try:
                content = httpx.Response(200, headers=headers, content=raw).content
            except Exception:
                content = raw
        elif truncated and headers.get("content-encoding"):
            _write_log_file(
                f"  response body for {_request_label(self._response.request)}:\n"
                f"    <{self._total} bytes of encoded data, too large to log>"
            )
            return
        body = _format_body(content, content_type=headers.get("content-type"), truncated=truncated)
        _write_log_file("\n".join([f"  response body for {_request_label(self._response.request)}:", *body]))


def _log_response_details(response: httpx.Response) -> None:
    if _log_file is None:
        return
    _write_log_file("\n".join(["  response headers:", *_format_headers(response.headers)]))
    stream = response.stream
    if isinstance(stream, httpx.AsyncByteStream):
        response.stream = _TeeResponseStream(response, stream)


def _print_lines(lines: Sequence[str]) -> None:
    for line in lines:
        _debug_print(f"[muted]debug[/muted] {line}")


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
    if _log_file_path:
        log_debug_note(f"writing full log (headers + bodies) to {_log_file_path}")


def log_debug_note(message: str) -> None:
    _debug_print(f"[muted]debug[/muted] {escape_rich_markup(message)}")


async def _on_request(request: httpx.Request) -> None:
    if not _enabled:
        return
    request.extensions[_START_EXTENSION] = time.perf_counter()
    _print_lines(render_request_lines(request, base_url=_base_url))
    _log_request_details(request)


async def _on_response(response: httpx.Response) -> None:
    if not _enabled:
        return
    start = response.request.extensions.get(_START_EXTENSION)
    elapsed: float | None
    if isinstance(start, (int, float)):
        elapsed = time.perf_counter() - float(start)
    else:
        elapsed = None
    _print_lines(render_response_lines(response, elapsed=elapsed))
    _log_response_details(response)
    _debug_print()


class CliDebugLogFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            return not is_noisy_log_message(record.getMessage())
        except Exception:
            return True


def _traceback_text(record: logging.LogRecord) -> str | None:
    exc_info = record.exc_info
    if not exc_info or exc_info[0] is None:
        return None
    return "".join(traceback.format_exception(*exc_info)).rstrip()


class CliDebugLogHandler(logging.Handler):
    @override
    def emit(self, record: logging.LogRecord) -> None:
        if not _enabled:
            return
        try:
            message = sanitize_debug_log_message(record.getMessage())
            level = record.levelname.lower()
            style = {
                "debug": "muted",
                "info": "info",
                "warning": "warning",
                "error": "error",
                "critical": "error",
            }.get(level, "muted")
            name = record.name.removeprefix("together.").removeprefix("together")
            _debug_print(
                f"[muted]log[/muted]  [{style}]{escape_rich_markup(level)}[/{style}] "
                f"[dim]{escape_rich_markup(name)}[/dim] {escape_rich_markup(message)}"
            )
            tb = _traceback_text(record)
            if tb:
                _debug_print(f"[muted]log[/muted]  [dim]{escape_rich_markup(sanitize_debug_log_message(tb))}[/dim]")
        except Exception:
            self.handleError(record)


def install_http_debug_hooks(http_client: httpx.AsyncClient) -> None:
    hooks = http_client.event_hooks
    request_hooks = hooks.setdefault("request", [])
    response_hooks = hooks.setdefault("response", [])
    if _on_request not in request_hooks:
        request_hooks.append(_on_request)
    if _on_response not in response_hooks:
        response_hooks.append(_on_response)


def setup_cli_debug_logging() -> None:
    global _enabled, _saved_httpx_level, _saved_together_level, _saved_together_propagate, _saved_together_log_env
    if _saved_together_log_env is None:
        env_value = os.environ.get("TOGETHER_LOG")
        _saved_together_log_env = ("TOGETHER_LOG" in os.environ, env_value or "")
    os.environ.setdefault("TOGETHER_LOG", "debug")
    _enabled = True
    if _log_file is None:
        _open_log_file()
    set_cli_debug_console_redirect(True)

    httpx_logger = logging.getLogger("httpx")
    together_logger = logging.getLogger("together")
    _saved_httpx_level = httpx_logger.level
    _saved_together_level = together_logger.level
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
    global \
        _enabled, \
        _base_url, \
        _saved_httpx_level, \
        _saved_together_level, \
        _saved_together_propagate, \
        _saved_together_log_env
    log_path = _log_file_path
    _enabled = False
    _base_url = ""
    set_cli_debug_console_redirect(False)
    _close_log_file()
    if log_path:
        error_console.print(f"[muted]debug[/muted] full log written to {escape_rich_markup(log_path)}", soft_wrap=True)

    together_logger = logging.getLogger("together")
    together_logger.handlers = [
        handler for handler in together_logger.handlers if not isinstance(handler, CliDebugLogHandler)
    ]
    if _saved_together_propagate is not None:
        together_logger.propagate = _saved_together_propagate
        _saved_together_propagate = None
    if _saved_together_level is not None:
        together_logger.setLevel(_saved_together_level)
        _saved_together_level = None

    if _saved_httpx_level is not None:
        logging.getLogger("httpx").setLevel(_saved_httpx_level)
        _saved_httpx_level = None

    if _saved_together_log_env is not None:
        was_set, value = _saved_together_log_env
        if was_set:
            os.environ["TOGETHER_LOG"] = value
        else:
            os.environ.pop("TOGETHER_LOG", None)
        _saved_together_log_env = None


def format_timeout_for_display(timeout: Union[float, httpx.Timeout, None]) -> str:
    return _format_timeout(timeout)


def format_duration_for_display(seconds: float) -> str:
    return _format_duration(seconds)
