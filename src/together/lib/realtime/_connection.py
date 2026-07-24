from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Dict, Mapping, Iterator, Optional, AsyncIterator

import httpx

from ._types import (
    DEFAULT_AUDIO_FORMAT,
    TurnDetectionParam,
    echo_event,
    clear_event,
    append_event,
    commit_event,
    parse_server_event,
    session_update_event,
)

if TYPE_CHECKING:
    from websockets.sync.client import ClientConnection as SyncClientConnection
    from websockets.asyncio.client import ClientConnection as AsyncClientConnection

    from ..._client import Together, AsyncTogether

__all__ = [
    "RealtimeConnection",
    "AsyncRealtimeConnection",
    "RealtimeConnectionManager",
    "AsyncRealtimeConnectionManager",
    "build_realtime_url",
    "build_realtime_headers",
    "handshake_status_of",
]

_INSTALL_HINT = 'The realtime API requires the `websockets` package; install it with `uv add "together[realtime]"`'


def _require_websockets() -> None:
    import importlib.util

    if importlib.util.find_spec("websockets") is None:
        raise RuntimeError(_INSTALL_HINT)


def handshake_status_of(exc: BaseException) -> Optional[int]:
    """HTTP status of a rejected WebSocket handshake, if the exception carries one."""
    try:
        from websockets.exceptions import InvalidStatus
    except ImportError:
        return None
    if isinstance(exc, InvalidStatus):
        response = getattr(exc, "response", None)
        return getattr(response, "status_code", None)
    return None


def build_realtime_url(
    base_url: httpx.URL,
    *,
    model: str,
    input_audio_format: str = DEFAULT_AUDIO_FORMAT,
    turn_detection: Optional[TurnDetectionParam] = None,
    extra_query: Optional[Mapping[str, Any]] = None,
) -> str:
    """Derive the wss:// realtime URL from the client's HTTP base_url.

    The model MUST be in the query string before any audio is appended —
    without it the server queues appends and never starts the session.
    """
    scheme = {"https": "wss", "http": "ws"}.get(base_url.scheme, base_url.scheme)
    path = base_url.path.rstrip("/") + "/realtime"
    params: Dict[str, Any] = {"model": model, "input_audio_format": input_audio_format}
    if turn_detection:
        detection = dict(turn_detection)
        detection_type = detection.pop("type", None)
        if detection_type is not None:
            params["turn_detection"] = detection_type
        params.update(detection)
    if extra_query:
        params.update(dict(extra_query))
    url = base_url.copy_with(scheme=scheme, path=path, params=params)
    return str(url)


def build_realtime_headers(
    auth_headers: Mapping[str, str],
    *,
    extra_headers: Optional[Mapping[str, str]] = None,
) -> Dict[str, str]:
    headers: Dict[str, str] = {**auth_headers, "OpenAI-Beta": "realtime=v1"}
    if extra_headers:
        headers.update(extra_headers)
    return headers


def _session_config(
    *,
    language: Optional[str],
    prompt: Optional[str],
    rolling_prompt: Optional[bool],
    energy_gate_rms: Optional[float],
    session_params: Optional[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Session-level params delivered via `transcription_session.updated`."""
    config: Dict[str, Any] = {}
    if language is not None:
        config["language"] = language
    if prompt is not None:
        config["prompt"] = prompt
    if rolling_prompt is not None:
        config["rolling_prompt"] = rolling_prompt
    if energy_gate_rms is not None:
        config["energy_gate_rms"] = energy_gate_rms
    if session_params:
        config.update(dict(session_params))
    return config


class _InputAudioBuffer:
    """`conn.input_audio_buffer.append/commit/clear` helpers (sync)."""

    def __init__(self, connection: RealtimeConnection) -> None:
        self._connection = connection

    def append(self, pcm: bytes) -> None:
        self._connection.send(append_event(pcm))

    def commit(self) -> None:
        self._connection.send(commit_event())

    def clear(self) -> None:
        self._connection.send(clear_event())


class RealtimeConnection:
    """A live, typed realtime WebSocket connection (no retry logic).

    Iterate to receive parsed server events; use `send` / `input_audio_buffer`
    helpers to talk to the server. Audio is always sent base64-encoded inside
    `input_audio_buffer.append` — the server terminates sessions on binary frames.
    """

    def __init__(self, ws: SyncClientConnection) -> None:
        self._ws = ws
        self.input_audio_buffer = _InputAudioBuffer(self)

    def send(self, event: Mapping[str, Any]) -> None:
        self._ws.send(json.dumps(dict(event)))

    def recv(self, timeout: Optional[float] = None) -> object:
        return parse_server_event(self._ws.recv(timeout=timeout))

    def session_update(self, session: Mapping[str, Any]) -> None:
        self.send(session_update_event(session))

    def echo(self, echo_id: Any = None) -> None:
        self.send(echo_event(echo_id=echo_id))

    def close(self) -> None:
        self._ws.close()

    def __iter__(self) -> Iterator[object]:
        while True:
            try:
                yield self.recv()
            except Exception:
                return


class _AsyncInputAudioBuffer:
    """`conn.input_audio_buffer.append/commit/clear` helpers (async)."""

    def __init__(self, connection: AsyncRealtimeConnection) -> None:
        self._connection = connection

    async def append(self, pcm: bytes) -> None:
        await self._connection.send(append_event(pcm))

    async def commit(self) -> None:
        await self._connection.send(commit_event())

    async def clear(self) -> None:
        await self._connection.send(clear_event())


class AsyncRealtimeConnection:
    """Async counterpart of RealtimeConnection."""

    def __init__(self, ws: AsyncClientConnection) -> None:
        self._ws = ws
        self.input_audio_buffer = _AsyncInputAudioBuffer(self)

    def is_closing(self) -> bool:
        """True once the close handshake has started in either direction.

        A graceful server close can stall for the server's close_timeout when
        the client is mid-burst; callers polling recv() should treat CLOSING
        as connection-lost instead of waiting the handshake out.
        """
        from websockets.protocol import State

        return self._ws.state is not State.OPEN

    @property
    def close_code(self) -> Optional[int]:
        """WebSocket close code once the connection has closed (None while open)."""
        return getattr(self._ws, "close_code", None)

    async def send(self, event: Mapping[str, Any]) -> None:
        await self._ws.send(json.dumps(dict(event)))

    async def recv(self) -> object:
        return parse_server_event(await self._ws.recv())

    async def session_update(self, session: Mapping[str, Any]) -> None:
        await self.send(session_update_event(session))

    async def echo(self, echo_id: Any = None) -> None:
        await self.send(echo_event(echo_id=echo_id))

    async def close(self) -> None:
        await self._ws.close()

    def __aiter__(self) -> AsyncIterator[object]:
        return self._iterate()

    async def _iterate(self) -> AsyncIterator[object]:
        while True:
            try:
                yield await self.recv()
            except Exception:
                return


class RealtimeConnectionManager:
    """Context manager returned by `client.beta.realtime.connect(...)` (sync)."""

    def __init__(
        self,
        *,
        client: Together,
        model: str,
        input_audio_format: str = DEFAULT_AUDIO_FORMAT,
        turn_detection: Optional[TurnDetectionParam] = None,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        rolling_prompt: Optional[bool] = None,
        energy_gate_rms: Optional[float] = None,
        session_params: Optional[Mapping[str, Any]] = None,
        extra_query: Optional[Mapping[str, Any]] = None,
        extra_headers: Optional[Mapping[str, str]] = None,
        open_timeout: Optional[float] = 10.0,
    ) -> None:
        self._client = client
        self._model = model
        self._input_audio_format = input_audio_format
        self._turn_detection = turn_detection
        self._session_config = _session_config(
            language=language,
            prompt=prompt,
            rolling_prompt=rolling_prompt,
            energy_gate_rms=energy_gate_rms,
            session_params=session_params,
        )
        self._extra_query = extra_query
        self._extra_headers = extra_headers
        self._open_timeout = open_timeout
        self._connection: Optional[RealtimeConnection] = None

    def connect(self) -> RealtimeConnection:
        _require_websockets()
        from websockets.sync.client import connect as ws_connect

        url = build_realtime_url(
            self._client.base_url,
            model=self._model,
            input_audio_format=self._input_audio_format,
            turn_detection=self._turn_detection,
            extra_query=self._extra_query,
        )
        headers = build_realtime_headers(self._client.auth_headers, extra_headers=self._extra_headers)
        ws = ws_connect(url, additional_headers=headers, open_timeout=self._open_timeout)
        self._connection = RealtimeConnection(ws)
        if self._session_config:
            self._connection.session_update(self._session_config)
        return self._connection

    def __enter__(self) -> RealtimeConnection:
        return self.connect()

    def __exit__(self, *_exc: object) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None


class AsyncRealtimeConnectionManager:
    """Awaitable context manager returned by `client.beta.realtime.connect(...)` (async)."""

    def __init__(
        self,
        *,
        client: AsyncTogether,
        model: str,
        input_audio_format: str = DEFAULT_AUDIO_FORMAT,
        turn_detection: Optional[TurnDetectionParam] = None,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        rolling_prompt: Optional[bool] = None,
        energy_gate_rms: Optional[float] = None,
        session_params: Optional[Mapping[str, Any]] = None,
        extra_query: Optional[Mapping[str, Any]] = None,
        extra_headers: Optional[Mapping[str, str]] = None,
        open_timeout: Optional[float] = 10.0,
    ) -> None:
        self._client = client
        self._model = model
        self._input_audio_format = input_audio_format
        self._turn_detection = turn_detection
        self._session_config = _session_config(
            language=language,
            prompt=prompt,
            rolling_prompt=rolling_prompt,
            energy_gate_rms=energy_gate_rms,
            session_params=session_params,
        )
        self._extra_query = extra_query
        self._extra_headers = extra_headers
        self._open_timeout = open_timeout
        self._connection: Optional[AsyncRealtimeConnection] = None

    async def connect(self) -> AsyncRealtimeConnection:
        _require_websockets()
        from websockets.asyncio.client import connect as ws_connect

        url = build_realtime_url(
            self._client.base_url,
            model=self._model,
            input_audio_format=self._input_audio_format,
            turn_detection=self._turn_detection,
            extra_query=self._extra_query,
        )
        headers = build_realtime_headers(self._client.auth_headers, extra_headers=self._extra_headers)
        ws = await ws_connect(url, additional_headers=headers, open_timeout=self._open_timeout)
        self._connection = AsyncRealtimeConnection(ws)
        if self._session_config:
            await self._connection.session_update(self._session_config)
        return self._connection

    async def __aenter__(self) -> AsyncRealtimeConnection:
        return await self.connect()

    async def __aexit__(self, *_exc: object) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None
