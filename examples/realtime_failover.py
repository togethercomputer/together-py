#!/usr/bin/env python3
"""Realtime transcription with failover across multiple endpoints.

Stream live audio to an endpoint; when it fails beyond recovery, resume on the
next endpoint in the ring, carrying over any speech that was never transcribed
so nothing is lost across the switch.

The SDK handles transient failures on a single endpoint internally (surfaced
only as Reconnecting/Reconnected events — nothing to handle). When an endpoint
is unrecoverable, SDK calls raise RealtimeConnectionError — including when the
server reports it cannot currently serve (exc.code == "no_healthy_workers",
raised immediately with no same-endpoint retry). One except handles both.
Moving to another endpoint is application code: the loop below handles failover.

Two things the successor needs from its predecessor, both carried below:
  * `pending_audio()` — speech the failed endpoint received but never
    transcribed. Replayed into the new session.
  * `context_prompt()` — tail of the delivered transcripts, passed as `prompt`
    so the new server decodes with the context the old one had. Without it the
    transcript degrades across the boundary.

What does NOT carry, because the successor is a fresh server session:
  * VAD *state* (position in the speech/silence hysteresis) — reconverges from
    the replayed audio, so a turn boundary at the switch may land slightly
    differently. VAD *config* carries fine: it is just SESSION_CFG.
  * item_id / session_id restart — turn ids are not comparable across endpoints.
  * Replayed audio is re-transcribed, so text can overlap what you already
    received; TranscriptCompleted.replayed marks it.

Usage:
    uv add "together[realtime]"
    export TOGETHER_API_KEY=...
    uv run ./examples/realtime_failover.py audio.wav   # 16 kHz mono s16le WAV
"""

from __future__ import annotations

import sys
import wave
import asyncio
import itertools
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

# Independent deployments of the same model. On failure the next entry takes
# over, wrapping around. Each entry is (base_url, model); base_url is the API
# root and may point at region-specific hosts so the ring entries share no
# failure domain.
ENDPOINTS = [
    ("https://api.together.ai/v1", "openai/whisper-large-v3-endpoint1"),
    ("https://api.together.ai/v1", "openai/whisper-large-v3-endpoint2"),
]

# False: ENDPOINTS order is a strict preference — every session starts on the
# first entry, later entries are pure standby.
# True: start each session on the next endpoint in turn, so all of them take
# live traffic and stay continuously exercised; the failover ring still works
# from wherever a session starts. Size each endpoint to absorb the full load
# alone, or an outage moves every session onto a saturated survivor.
SPREAD_SESSIONS = False
_ring = itertools.count()

SAMPLE_RATE = 16_000
CHUNK_BYTES = SAMPLE_RATE * 2 // 10  # 100 ms per append, like a live source
MAX_ATTEMPTS = 3 * len(ENDPOINTS)  # give up after several full ring cycles

# Every session in the ring is configured identically — defined once and spread
# into each one, so a failover cannot silently change transcription behaviour.
# Put language / turn_detection / energy_gate_rms / session_params here.
SESSION_CFG = {
    "sample_rate": SAMPLE_RATE,
    # Switch endpoints immediately on failure. Raise max_attempts to let the
    # SDK retry the same endpoint first.
    "reconnect": {"max_attempts": 0},
}


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
    carry_prompt = ""  # decode context the failed endpoint had built up
    position = 0  # progress through the source; survives endpoint switches

    start = next(_ring) % len(clients) if SPREAD_SESSIONS else 0

    for attempt in range(MAX_ATTEMPTS):
        client, model = clients[(start + attempt) % len(clients)]
        print(f"--- streaming to {model}")

        session = client.beta.realtime.transcription(
            model=model,
            # Prime the successor with what its predecessor already decoded.
            prompt=carry_prompt or None,
            event_callback=on_event,
            **SESSION_CFG,
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
            # keep its transcripts, take back the audio it never transcribed
            # and the context it had built, and move to the next endpoint.
            transcripts.extend(session.transcripts)
            carry_over = session.pending_audio()
            carry_prompt = session.context_prompt()
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
