#!/usr/bin/env python3
"""Realtime transcription of live audio.

Stream PCM audio as it is captured and receive interim text while a phrase
is being spoken, plus a finalized transcript per utterance. The WAV file
here stands in for a live source (microphone, phone call, meeting audio).

Usage:
    uv add "together[realtime]"
    export TOGETHER_API_KEY=...
    uv run ./examples/realtime_transcription.py audio.wav   # 16 kHz mono s16le WAV
"""

from __future__ import annotations

import sys
import wave
import asyncio
from pathlib import Path

from together import AsyncTogether
from together.realtime import (
    SessionStarted,
    TranscriptDelta,
    TranscriptCompleted,
    RealtimeSessionEvent,
)

MODEL = "openai/whisper-large-v3"

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
        print(f"final: {event.text}")


async def transcribe(audio: bytes) -> str:
    client = AsyncTogether()

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

        return await session.flush()  # finalize whatever was said last


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
