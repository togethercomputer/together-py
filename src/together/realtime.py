"""Public types for the realtime transcription API (`client.beta.realtime`).

Import events, options, and exceptions from here:

    from together.realtime import TranscriptCompleted, RealtimeConnectionError

This module is the stable import surface; the implementation lives in
`together.lib.realtime` and may be reorganized without notice.
"""

from .lib.realtime import (
    BufferGap as BufferGap,
    TurnEvent as TurnEvent,
    Reconnected as Reconnected,
    Reconnecting as Reconnecting,
    UnknownEvent as UnknownEvent,
    BufferOptions as BufferOptions,
    RealtimeError as RealtimeError,
    SessionStarted as SessionStarted,
    TranscriptDelta as TranscriptDelta,
    RealtimeLogprobs as RealtimeLogprobs,
    ReconnectOptions as ReconnectOptions,
    TranscriptFailed as TranscriptFailed,
    EchoResponseEvent as EchoResponseEvent,
    RealtimeErrorInfo as RealtimeErrorInfo,
    TranscriptionToken as TranscriptionToken,
    TurnDetectionParam as TurnDetectionParam,
    RealtimeServerEvent as RealtimeServerEvent,
    SessionCreatedEvent as SessionCreatedEvent,
    TranscriptCompleted as TranscriptCompleted,
    RealtimeSessionError as RealtimeSessionError,
    RealtimeSessionEvent as RealtimeSessionEvent,
    RealtimeConnectionError as RealtimeConnectionError,
    TranscriptionDeltaEvent as TranscriptionDeltaEvent,
    RealtimeIdleTimeoutError as RealtimeIdleTimeoutError,
    TranscriptionFailedEvent as TranscriptionFailedEvent,
    RealtimeInvalidStateError as RealtimeInvalidStateError,
    RealtimeBufferOverflowError as RealtimeBufferOverflowError,
    TranscriptionCompletedEvent as TranscriptionCompletedEvent,
    InputAudioBufferProcessedEvent as InputAudioBufferProcessedEvent,
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
