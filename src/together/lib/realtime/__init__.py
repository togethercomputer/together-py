"""Realtime transcription over WebSocket for the Together SDK.

Public import surface for the realtime package. Everything not exported here
is private and may change without notice.
"""

from ._types import (
    BufferGap,
    TurnEvent,
    Reconnected,
    Reconnecting,
    UnknownEvent,
    BufferOptions,
    SessionStarted,
    TranscriptDelta,
    RealtimeLogprobs,
    ReconnectOptions,
    TranscriptFailed,
    EchoResponseEvent,
    RealtimeErrorInfo,
    TranscriptionToken,
    TurnDetectionParam,
    RealtimeServerEvent,
    SessionCreatedEvent,
    TranscriptCompleted,
    RealtimeSessionEvent,
    TranscriptionDeltaEvent,
    TranscriptionFailedEvent,
    TranscriptionCompletedEvent,
    InputAudioBufferProcessedEvent,
)
from ._exceptions import (
    RealtimeError,
    RealtimeSessionError,
    RealtimeConnectionError,
    RealtimeIdleTimeoutError,
    RealtimeInvalidStateError,
    RealtimeBufferOverflowError,
)

__all__ = [
    # events (wire)
    "RealtimeServerEvent",
    "SessionCreatedEvent",
    "TranscriptionDeltaEvent",
    "TranscriptionCompletedEvent",
    "TranscriptionFailedEvent",
    "TurnEvent",
    "InputAudioBufferProcessedEvent",
    "EchoResponseEvent",
    "UnknownEvent",
    "RealtimeErrorInfo",
    "RealtimeLogprobs",
    "TranscriptionToken",
    # events (normalized session)
    "RealtimeSessionEvent",
    "SessionStarted",
    "TranscriptDelta",
    "TranscriptCompleted",
    "TranscriptFailed",
    "Reconnecting",
    "Reconnected",
    "BufferGap",
    # options
    "TurnDetectionParam",
    "ReconnectOptions",
    "BufferOptions",
    # exceptions
    "RealtimeError",
    "RealtimeConnectionError",
    "RealtimeSessionError",
    "RealtimeIdleTimeoutError",
    "RealtimeBufferOverflowError",
    "RealtimeInvalidStateError",
]
