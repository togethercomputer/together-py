#!/usr/bin/env python3
"""Realtime transcription that rides out failures on a single endpoint.

The SDK recovers from transient failures on its own: if the connection drops
mid-conversation, it reconnects with backoff and replays the speech the
server never transcribed — the application just keeps feeding audio. You'll
see Reconnecting/Reconnected events; there is nothing to handle.

Only when the endpoint stays unrecoverable past the retry budget do SDK
calls raise RealtimeConnectionError. To keep a conversation alive across
endpoint outages, add an endpoint ring on top — see
examples/realtime_failover.py.

Usage:
    uv add "together[realtime]"
    export TOGETHER_API_KEY=...
    uv run ./examples/realtime_single_endpoint_failover.py audio.wav   # 16 kHz mono s16le WAV
"""

from __future__ import annotations

import sys
import wave
import asyncio
from pathlib import Path

from together import AsyncTogether
from together.lib.realtime import (
    BufferGap,
    Reconnected,
    Reconnecting,
    SessionStarted,
    TranscriptDelta,
    TranscriptFailed,
    TranscriptCompleted,
    RealtimeSessionEvent,
)

MODEL = "openai/whisper-large-v3-endpoint1"

SAMPLE_RATE = 16_000
CHUNK_BYTES = SAMPLE_RATE * 2 // 10  # 100 ms per append, like a live source


def on_event(event: RealtimeSessionEvent) -> None:
    """Handle session events as they arrive."""
    if isinstance(event, SessionStarted):
        # Log the server-assigned session id — useful when correlating a
        # stream with server-side logs or support requests.
        print(f"session {event.session_id} started on {event.model}")
    elif isinstance(event, TranscriptDelta):
        print(f"interim: {event.text}", end="\r")
    elif isinstance(event, TranscriptCompleted):
        # `replayed` marks re-transcriptions of speech replayed after a
        # reconnect; they may overlap text you already received.
        marker = " (replayed)" if event.replayed else ""
        print(f"final: {event.text}{marker}")
    elif isinstance(event, Reconnecting):
        # Transient failure: the SDK is recovering on its own — no action
        # needed, shown here only to make the recovery visible.
        print(f"[reconnecting, attempt {event.attempt}: {event.reason}]")
    elif isinstance(event, Reconnected):
        print(f"[reconnected; {event.replayed_seconds:.1f}s of speech replayed]")
    elif isinstance(event, TranscriptFailed):
        # One utterance failed server-side; the session continues.
        print(f"[utterance failed: {event.message}]")
    elif isinstance(event, BufferGap):
        # Audio dropped beyond recovery — always announced, never silent.
        print(f"[gap: {event.dropped_seconds:.1f}s lost]")


async def transcribe(audio: bytes) -> str:
    client = AsyncTogether()

    # Default reconnect settings retry this endpoint with backoff; failures
    # you see as Reconnecting/Reconnected events are handled entirely by the
    # SDK, with un-transcribed speech replayed after each reconnect.
    async with client.beta.realtime.transcription(
        model=MODEL,
        sample_rate=SAMPLE_RATE,
        event_callback=on_event,
    ) as session:
        position = 0
        while position < len(audio):
            await session.append(audio[position : position + CHUNK_BYTES])
            position += CHUNK_BYTES
            await asyncio.sleep(0.1)  # simulate a live capture cadence

        return await session.flush()


def load_pcm(path: Path) -> bytes:
    with wave.open(str(path), "rb") as w:
        if (w.getnchannels(), w.getsampwidth(), w.getframerate()) != (1, 2, SAMPLE_RATE):
            raise SystemExit(f"expected mono 16-bit {SAMPLE_RATE} Hz WAV")
        return w.readframes(w.getnframes())


async def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    transcript = await transcribe(load_pcm(Path(sys.argv[1])))
    print(f"\nfull transcript: {transcript}")


if __name__ == "__main__":
    asyncio.run(main())
