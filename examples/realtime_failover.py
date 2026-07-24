#!/usr/bin/env python3
"""Realtime transcription with failover across multiple endpoints.

Stream live audio to a primary endpoint; when it fails beyond recovery,
resume on the next endpoint in the ring, carrying over any speech that was
never transcribed so nothing is lost across the switch.

The SDK handles transient failures on a single endpoint internally (surfaced
only as Reconnecting/Reconnected events — nothing to handle). When an endpoint
is unrecoverable, SDK calls raise RealtimeConnectionError — including when the
server reports it cannot currently serve (exc.code == "no_healthy_workers",
raised immediately with no same-endpoint retry). One except handles both.
Moving to another endpoint is application code: the loop below handles failover.

Usage:
    uv add "together[realtime]"
    export TOGETHER_API_KEY=...
    uv run ./examples/realtime_failover.py audio.wav   # 16 kHz mono s16le WAV
"""

from __future__ import annotations

import sys
import wave
import asyncio
from pathlib import Path

from together import AsyncTogether
from together.realtime import (
    BufferGap,
    SessionStarted,
    TranscriptDelta,
    TranscriptCompleted,
    RealtimeSessionEvent,
    RealtimeConnectionError,
)

# Independent deployments of the same model. Order = preference; on failure
# the next entry takes over, wrapping around. Each entry is (base_url, model);
# base_url is the API root and may point at region-specific hosts so the ring
# entries share no failure domain.
ENDPOINTS = [
    ("https://api.together.ai/v1", "openai/whisper-large-v3-endpoint1"),
    ("https://api.together.ai/v1", "openai/whisper-large-v3-endpoint2"),
]

SAMPLE_RATE = 16_000
CHUNK_BYTES = SAMPLE_RATE * 2 // 10  # 100 ms per append, like a live source
MAX_ATTEMPTS = 3 * len(ENDPOINTS)  # give up after several full ring cycles


def on_event(event: RealtimeSessionEvent) -> None:
    """Handle session events as they arrive."""
    if isinstance(event, SessionStarted):
        # Log the server-assigned session id — useful for correlating a session.
        print(f"session {event.session_id} started on {event.model}")
    elif isinstance(event, TranscriptDelta):
        print(f"interim: {event.text}", end="\r")
    elif isinstance(event, TranscriptCompleted):
        # `replayed` marks re-transcriptions of carried-over audio; they may
        # overlap text you already received.
        marker = " (replayed)" if event.replayed else ""
        print(f"final: {event.text}{marker}")
    elif isinstance(event, BufferGap):
        # Audio dropped beyond recovery.
        print(f"[gap: {event.dropped_seconds:.1f}s lost]")


async def transcribe_with_failover(audio: bytes) -> str:
    # One client per endpoint: base_url is client-level configuration.
    # Clients are lightweight config objects — nothing connects until a
    # session starts.
    clients = [(AsyncTogether(base_url=base_url), model) for base_url, model in ENDPOINTS]

    transcripts: list[str] = []
    carry_over = b""  # audio the failed endpoint received but never transcribed
    position = 0  # progress through the source; survives endpoint switches

    for attempt in range(MAX_ATTEMPTS):
        client, model = clients[attempt % len(clients)]
        print(f"--- streaming to {model}")

        session = client.beta.realtime.transcription(
            model=model,
            sample_rate=SAMPLE_RATE,
            event_callback=on_event,
            # Switch endpoints immediately on failure. Raise max_attempts to
            # let the SDK retry the same endpoint first.
            reconnect={"max_attempts": 0},
        )
        try:
            async with session:
                if carry_over:
                    # The un-transcribed speech from the failed endpoint is transmitted
                    # as fast as the connection allows, so the new endpoint catches up to live immediately.
                    await session.append(carry_over)

                while position < len(audio):
                    await session.append(audio[position : position + CHUNK_BYTES])
                    position += CHUNK_BYTES
                    await asyncio.sleep(0.1)  # simulate a live capture cadence
                transcripts.append(await session.flush())
                return " ".join(t for t in transcripts if t)
        except RealtimeConnectionError as exc:
            # Endpoint unrecoverable (incl. exc.code == "no_healthy_workers"):
            # keep its transcripts, take back the audio it never transcribed,
            # and move to the next endpoint.
            transcripts.extend(session.transcripts)
            carry_over = session.pending_audio()
            print(f"--- {model} failed ({exc}); carrying over {len(carry_over) / (SAMPLE_RATE * 2):.1f}s of audio")

    raise SystemExit("all endpoints failed repeatedly; giving up")


def load_pcm(path: Path) -> bytes:
    with wave.open(str(path), "rb") as w:
        if (w.getnchannels(), w.getsampwidth(), w.getframerate()) != (1, 2, SAMPLE_RATE):
            raise SystemExit(f"expected mono 16-bit {SAMPLE_RATE} Hz WAV")
        return w.readframes(w.getnframes())


async def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    transcript = await transcribe_with_failover(load_pcm(Path(sys.argv[1])))
    print(f"\nfull transcript: {transcript}")


if __name__ == "__main__":
    asyncio.run(main())
