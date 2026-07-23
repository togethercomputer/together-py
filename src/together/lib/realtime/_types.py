from __future__ import annotations

import json
import base64
from typing import Any, Dict, List, Union, Mapping, Optional, cast
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ..._utils import PropertyInfo
from ..._models import BaseModel, construct_type_unchecked

__all__ = [
    # audio formats
    "AUDIO_FORMATS",
    "bytes_per_second",
    # wire (server -> client) events
    "RealtimeErrorInfo",
    "RealtimeSessionInfo",
    "RealtimeLogprobs",
    "TranscriptionToken",
    "SessionCreatedEvent",
    "TranscriptionDeltaEvent",
    "TranscriptionCompletedEvent",
    "TranscriptionFailedEvent",
    "TurnEvent",
    "InputAudioBufferProcessedEvent",
    "EchoResponseEvent",
    "UnknownEvent",
    "RealtimeServerEvent",
    "parse_server_event",
    # client -> server event builders
    "append_event",
    "commit_event",
    "clear_event",
    "session_update_event",
    "echo_event",
    # options
    "TurnDetectionParam",
    "ReconnectOptions",
    "BufferOptions",
    # normalized session events
    "SessionStarted",
    "TranscriptDelta",
    "TranscriptCompleted",
    "TranscriptFailed",
    "Reconnecting",
    "Reconnected",
    "BufferGap",
    "RealtimeSessionEvent",
]

# ---------------------------------------------------------------------------
# Audio formats
#
# Bytes/second for each `input_audio_format` accepted by the server. Note the
# bare `pcm16`/`pcm_s16`/`pcm_s16le` aliases are 24 kHz on the server side —
# the SDK defaults to the explicit `pcm_s16le_16000` to avoid that surprise.
# ---------------------------------------------------------------------------

AUDIO_FORMATS: Dict[str, int] = {
    "pcm_s16le_8000": 8_000 * 2,
    "pcm_s16le_16000": 16_000 * 2,
    "pcm_s16le_24000": 24_000 * 2,
    "pcm16": 24_000 * 2,
    "pcm_s16": 24_000 * 2,
    "pcm_s16le": 24_000 * 2,
}

DEFAULT_AUDIO_FORMAT = "pcm_s16le_16000"


def bytes_per_second(input_audio_format: str) -> int:
    try:
        return AUDIO_FORMATS[input_audio_format]
    except KeyError:
        raise ValueError(
            f"Unsupported input_audio_format {input_audio_format!r}; expected one of {sorted(AUDIO_FORMATS)}"
        ) from None


def sample_rate_of(input_audio_format: str) -> int:
    return bytes_per_second(input_audio_format) // 2


# ---------------------------------------------------------------------------
# Wire events (server -> client)
#
# Field presence is deliberately loose: the server emits several shapes for
# the same event type (e.g. `completed` without item_id/start/duration on some
# backend paths), and events must parse under both pydantic v1 and v2 — hence
# construct_type_unchecked + explicit dispatch instead of strict validation.
# ---------------------------------------------------------------------------


class RealtimeErrorInfo(BaseModel):
    message: Optional[str] = None
    type: Optional[str] = None
    param: Optional[str] = None
    code: Optional[str] = None


class RealtimeSessionInfo(BaseModel):
    id: Optional[str] = None
    object: Optional[str] = None
    model: Optional[str] = None
    modalities: Optional[Any] = None


class SessionCreatedEvent(BaseModel):
    type: Literal["session.created"]
    event_id: Optional[str] = None
    session: Optional[RealtimeSessionInfo] = None


# Per-token quality signals the server may attach to delta/completed frames
# (off the OpenAI spec). Present only when the server includes them; all fields
# optional so frames without them still parse.
class RealtimeLogprobs(BaseModel):
    avg_logprob: Optional[float] = None
    token_logprobs: Optional[List[float]] = None
    """Parallel to token_texts: token_logprobs[i] is the logprob of token_texts[i]."""
    token_texts: Optional[List[str]] = None


class TranscriptionToken(BaseModel):
    token_id: Optional[int] = None
    text: Optional[str] = None
    confidence: Optional[float] = None
    """Softmax probability of the emitted token (exp of its logprob)."""


class TranscriptionDeltaEvent(BaseModel):
    type: Literal["conversation.item.input_audio_transcription.delta"]
    item_id: Optional[str] = None
    delta: str = ""
    start: Optional[float] = None
    """Server-side consumed-speech clock — NOT a position on the appended-audio
    timeline (silence is skipped); do not use for buffer accounting."""
    duration: Optional[float] = None
    logprobs: Optional[RealtimeLogprobs] = None
    tokens: Optional[List[TranscriptionToken]] = None


class TranscriptionCompletedEvent(BaseModel):
    type: Literal["conversation.item.input_audio_transcription.completed"]
    item_id: Optional[str] = None
    transcript: str = ""
    start: Optional[float] = None
    """See TranscriptionDeltaEvent.start — informational only."""
    duration: Optional[float] = None
    logprobs: Optional[RealtimeLogprobs] = None
    tokens: Optional[List[TranscriptionToken]] = None


class TranscriptionFailedEvent(BaseModel):
    type: Literal["conversation.item.input_audio_transcription.failed"]
    item_id: Optional[str] = None
    event_type: Optional[str] = None
    """Present on per-turn failures ("delta"/"completed"); absent on fatal
    session errors (which are followed by a server-side close)."""
    error: Optional[RealtimeErrorInfo] = None
    start: Optional[float] = None
    """Stream position of the dropped span (with duration), when the server
    provides it — lets a client locate the audio it can slice and resume."""
    duration: Optional[float] = None

    @property
    def is_fatal(self) -> bool:
        return self.event_type is None


class TurnEvent(BaseModel):
    type: Literal[
        "conversation.item.input_audio_transcription.start_of_turn",
        "conversation.item.input_audio_transcription.end_of_turn",
        "conversation.item.input_audio_transcription.eager_end_of_turn",
        "conversation.item.input_audio_transcription.turn_resumed",
    ]
    item_id: Optional[str] = None
    transcript: Optional[str] = None
    end_of_turn_confidence: Optional[float] = None


class InputAudioBufferProcessedEvent(BaseModel):
    """Trim-safety watermark on the appended-audio timeline (newer servers only).

    Means: the server has finished all decodes covering audio at or before
    `processed_ms` and will never re-read earlier bytes. It does NOT imply a
    transcript exists for all of that audio.
    """

    type: Literal["input_audio_buffer.processed"]
    processed_ms: float


class EchoResponseEvent(BaseModel):
    type: Literal["echo.response"]
    echo_id: Optional[Any] = None
    client_sent_at: Optional[Any] = None
    server_received_at: Optional[float] = None
    server_sent_at: Optional[float] = None
    payload: Optional[Any] = None


class UnknownEvent(BaseModel):
    """Forward-compat catch-all for event types this SDK version doesn't know."""

    type: str
    data: Dict[str, Any]


# Public type alias for annotating connect()-level raw events. Parse dispatch
# uses the _EVENT_TYPES dict below, NOT this union (repo convention: no native
# pydantic discriminators, they differ across v1/v2) — don't wire it up or
# delete it; it exists purely as a typing surface for SDK consumers.
RealtimeServerEvent: TypeAlias = Annotated[
    Union[
        SessionCreatedEvent,
        TranscriptionDeltaEvent,
        TranscriptionCompletedEvent,
        TranscriptionFailedEvent,
        TurnEvent,
        InputAudioBufferProcessedEvent,
        EchoResponseEvent,
        UnknownEvent,
    ],
    PropertyInfo(discriminator="type"),
]

_EVENT_TYPES: Dict[str, type] = {
    "session.created": SessionCreatedEvent,
    "conversation.item.input_audio_transcription.delta": TranscriptionDeltaEvent,
    "conversation.item.input_audio_transcription.completed": TranscriptionCompletedEvent,
    "conversation.item.input_audio_transcription.failed": TranscriptionFailedEvent,
    "conversation.item.input_audio_transcription.start_of_turn": TurnEvent,
    "conversation.item.input_audio_transcription.end_of_turn": TurnEvent,
    "conversation.item.input_audio_transcription.eager_end_of_turn": TurnEvent,
    "conversation.item.input_audio_transcription.turn_resumed": TurnEvent,
    "input_audio_buffer.processed": InputAudioBufferProcessedEvent,
    "echo.response": EchoResponseEvent,
}


def parse_server_event(payload: Union[str, bytes, Mapping[str, Any]]) -> object:
    """Parse a wire frame into a typed server event.

    Dispatches explicitly on `type` (deterministic under both pydantic majors)
    and falls back to UnknownEvent for unrecognized types.
    """
    raw: Any = json.loads(payload) if isinstance(payload, (str, bytes)) else dict(payload)
    if not isinstance(raw, dict):
        return UnknownEvent(type="<non-object>", data={"value": raw})
    data = cast("Dict[str, Any]", raw)
    event_type = data.get("type")
    model = _EVENT_TYPES.get(event_type) if isinstance(event_type, str) else None
    if model is None:
        return UnknownEvent(type=str(event_type), data=data)
    return cast(object, construct_type_unchecked(value=data, type_=model))


# ---------------------------------------------------------------------------
# Client events (client -> server) — plain dict builders
# ---------------------------------------------------------------------------


def append_event(pcm: Union[bytes, bytearray, memoryview]) -> Dict[str, Any]:
    return {"type": "input_audio_buffer.append", "audio": base64.b64encode(bytes(pcm)).decode("ascii")}


def commit_event() -> Dict[str, Any]:
    return {"type": "input_audio_buffer.commit"}


def clear_event() -> Dict[str, Any]:
    return {"type": "input_audio_buffer.clear"}


def session_update_event(session: Mapping[str, Any]) -> Dict[str, Any]:
    # The server listens for the ".updated" variant (not ".update").
    return {"type": "transcription_session.updated", "session": dict(session)}


def echo_event(echo_id: Any = None, payload: Any = None) -> Dict[str, Any]:
    event: Dict[str, Any] = {"type": "echo"}
    if echo_id is not None:
        event["echo_id"] = echo_id
    if payload is not None:
        event["payload"] = payload
    return event


# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------


class TurnDetectionParam(TypedDict, total=False):
    type: Required[Literal["server_vad", "none"]]
    threshold: float
    min_silence_duration_ms: int
    min_speech_duration_ms: int
    max_speech_duration_s: float
    speech_pad_ms: int
    # Deepgram backends
    eot_threshold: float
    eot_timeout_ms: int
    eager_eot_threshold: float


class ReconnectOptions(TypedDict, total=False):
    max_attempts: int
    """Maximum consecutive same-endpoint reconnect attempts before giving up
    (default 2). Kept low because a websocket drop is usually a transient blip;
    if a couple quick reconnects don't recover, a RealtimeConnectionError is
    raised so a failover loop can rotate endpoints. Failures the server reports
    as terminal (code='no_healthy_workers') bypass this and raise immediately."""
    max_elapsed: float
    """Maximum seconds spent in a single reconnect episode (default 120)."""
    backoff_initial: float
    """Initial backoff delay in seconds (default 0.5)."""
    backoff_max: float
    """Backoff delay ceiling in seconds (default 15)."""


class BufferOptions(TypedDict, total=False):
    max_seconds: float
    """Outer bound on retained audio per session (default 120)."""
    overflow: Literal["drop_oldest", "error"]
    """What to do when retained audio exceeds max_seconds (default drop_oldest,
    which surfaces a BufferGap event)."""
    replay_margin: float
    """Optional pre-roll rewound before the last transcribed position when
    replaying (default 0.0)."""
    max_replay_seconds: Optional[float]
    """Replay starts at max(head - max_replay_seconds, last transcribed
    position). Default 5.0; 0 resumes live without any replay; None removes
    the cap (replay the full untranscribed window)."""


# ---------------------------------------------------------------------------
# Normalized session events (Layer 2)
#
# segment_id and audio_start/audio_end are SDK-computed from global appended
# audio offsets: stable across reconnects, unlike server item_ids.
# ---------------------------------------------------------------------------


class SessionStarted(BaseModel):
    type: Literal["session.started"] = "session.started"
    session_id: Optional[str] = None
    model: Optional[str] = None
    epoch: int = 0


class TranscriptDelta(BaseModel):
    type: Literal["transcript.delta"] = "transcript.delta"
    segment_id: str
    text: str
    audio_start: Optional[float] = None
    audio_end: Optional[float] = None
    replayed: bool = False
    logprobs: Optional[RealtimeLogprobs] = None
    tokens: Optional[List[TranscriptionToken]] = None
    raw: Optional[TranscriptionDeltaEvent] = None


class TranscriptCompleted(BaseModel):
    type: Literal["transcript.completed"] = "transcript.completed"
    segment_id: str
    text: str
    audio_start: Optional[float] = None
    audio_end: Optional[float] = None
    replayed: bool = False
    logprobs: Optional[RealtimeLogprobs] = None
    tokens: Optional[List[TranscriptionToken]] = None
    raw: Optional[TranscriptionCompletedEvent] = None


class TranscriptFailed(BaseModel):
    type: Literal["transcript.failed"] = "transcript.failed"
    segment_id: Optional[str] = None
    message: Optional[str] = None
    replayed: bool = False
    raw: Optional[TranscriptionFailedEvent] = None


class Reconnecting(BaseModel):
    type: Literal["reconnecting"] = "reconnecting"
    attempt: int
    reason: str
    model: Optional[str] = None
    """The endpoint this attempt will target (rotates through fallbacks)."""


class Reconnected(BaseModel):
    type: Literal["reconnected"] = "reconnected"
    attempt: int
    replayed_seconds: float
    model: Optional[str] = None
    """The endpoint now serving the session (differs from the primary when a
    fallback model took over)."""


class BufferGap(BaseModel):
    type: Literal["buffer.gap"] = "buffer.gap"
    dropped_seconds: float
    reason: str


RealtimeSessionEvent: TypeAlias = Union[
    SessionStarted,
    TranscriptDelta,
    TranscriptCompleted,
    TranscriptFailed,
    Reconnecting,
    Reconnected,
    BufferGap,
]
