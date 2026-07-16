#!/usr/bin/env python3
"""Realtime transcription with endpoint failover.

Run against a primary endpoint; when it fails beyond recovery, resume on the
next endpoint in the ring, carrying over any audio that was never transcribed
so no speech is lost across the switch.

Division of labor:
  - The SDK handles transient failures on the CURRENT endpoint internally
    (reconnect, backoff, replay) — you'll see Reconnecting/Reconnected events.
  - When an endpoint is unrecoverable, SDK calls raise RealtimeConnectionError.
    Moving to another endpoint is application code: the loop below.

Usage:
    pip install "together[realtime]"
    export TOGETHER_API_KEY=...
    python examples/realtime_failover.py audio.wav   # 16 kHz mono s16le WAV
"""

from __future__ import annotations

import sys
import wave
import asyncio
from pathlib import Path

from together import AsyncTogether
from together.lib.realtime import (
    BufferGap,
    SessionStarted,
    TranscriptCompleted,
    RealtimeSessionEvent,
    RealtimeConnectionError,
)

# Independent deployments of the same model, addressed directly (per-cluster
# URLs) so the two ring entries share no failure domain. Order = preference;
# on failure the next entry takes over, wrapping around.
#
# base_url is the API root and must end at /v1 — the SDK appends the
# /realtime path (and any other resource paths) itself.
ENDPOINTS = [
    (
        "https://funkyfalcon.api.together.ai/pool/ipop-4-openai-whisper-large-v3-92f607e9/v1",
        "together_sso/openai/whisper-large-v3-47df6eb0",
    ),
    (
        "https://trickytrout.api.together.ai/pool/ipop-4-openai-whisper-large-v3-e6e3a747/v1",
        "together_sso/openai/whisper-large-v3-e151bfbf",
    ),
]

SAMPLE_RATE = 16_000
CHUNK_BYTES = SAMPLE_RATE * 2 // 10  # 100 ms per append, like a live source
MAX_ATTEMPTS = 3 * len(ENDPOINTS)  # give up after several full ring cycles


def on_event(event: RealtimeSessionEvent) -> None:
    """Handle transcripts as they arrive (called for every session event)."""
    if isinstance(event, SessionStarted):
        # Log the server-assigned session id — invaluable when correlating a
        # stream with server-side logs or support requests.
        print(f"session {event.session_id} started on {event.model}")
    elif isinstance(event, TranscriptCompleted):
        # `replayed` marks re-transcriptions of carried-over audio; they may
        # overlap text you already received.
        marker = " (replayed)" if event.replayed else ""
        print(f"final: {event.text}{marker}")
    elif isinstance(event, BufferGap):
        # Audio dropped beyond recovery — always announced, never silent.
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
        print(f"--- streaming to {model} via {client.base_url.host}")

        session = client.realtime.transcription(
            model=model,
            sample_rate=SAMPLE_RATE,
            event_callback=on_event,
            # Fail fast: hand a dead endpoint straight to this loop instead of
            # retrying it. Raise max_attempts to retry in place before switching.
            reconnect={"max_attempts": 0},
        )
        try:
            async with session:
                if carry_over:
                    # One append, no pacing: the un-transcribed speech from the
                    # failed endpoint is transmitted as fast as the connection
                    # allows, so the new endpoint catches up to live immediately.
                    await session.append(carry_over)

                while position < len(audio):
                    await session.append(audio[position : position + CHUNK_BYTES])
                    position += CHUNK_BYTES
                    await asyncio.sleep(0.1)  # simulate a live capture cadence

                transcripts.append(await session.flush())
                return " ".join(t for t in transcripts if t)

        except RealtimeConnectionError as exc:
            # Endpoint is unrecoverable: keep its transcripts, take back the
            # audio it never transcribed, and move to the next endpoint.
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
