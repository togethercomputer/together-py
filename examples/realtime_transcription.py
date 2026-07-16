#!/usr/bin/env python3
"""Realtime transcription over WebSocket with automatic reconnection.

Streams a 16 kHz mono PCM WAV (or raw PCM) file to the Together realtime API
and prints interim and final transcripts. The session survives connection
drops: buffered audio is replayed from the last confirmed transcript.

Usage:
    pip install "together[realtime]"
    export TOGETHER_API_KEY=...
    python examples/realtime_transcription.py audio.wav
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
    TranscriptDelta,
    TranscriptCompleted,
)

CHUNK_MS = 40
SAMPLE_RATE = 16_000
BYTES_PER_SECOND = SAMPLE_RATE * 2


def load_pcm(path: Path) -> bytes:
    if path.suffix.lower() != ".wav":
        return path.read_bytes()
    with wave.open(str(path), "rb") as wav:
        if wav.getnchannels() != 1 or wav.getsampwidth() != 2 or wav.getframerate() != SAMPLE_RATE:
            raise SystemExit("expected mono 16-bit 16 kHz WAV (resample first)")
        return wav.readframes(wav.getnframes())


async def main() -> None:
    audio = load_pcm(Path(sys.argv[1]))
    client = AsyncTogether()

    async with client.realtime.transcription(
        # model="together_sso/openai/whisper-large-v3-47df6eb0",
        model="together_sso/openai/whisper-large-v3-e151bfbf",
        sample_rate=SAMPLE_RATE,
    ) as session:

        async def feed() -> None:
            chunk_bytes = BYTES_PER_SECOND * CHUNK_MS // 1000
            for start in range(0, len(audio), chunk_bytes):
                await session.append(audio[start : start + chunk_bytes])
                await asyncio.sleep(CHUNK_MS / 1000)  # pace like a live mic
            print("\n[audio fully sent — draining transcripts]")

        feeder = asyncio.create_task(feed())

        async def consume() -> None:
            async for event in session:
                if isinstance(event, TranscriptDelta):
                    # print(f"\r… {event.text}", end="", flush=True)
                    pass
                elif isinstance(event, TranscriptCompleted):
                    # marker = " (replayed)" if event.replayed else ""
                    # print(f"\rfinal: {event.text}{marker}")
                    print(event.text)
                elif isinstance(event, Reconnecting):
                    # print(f"\n[reconnecting: {event.reason} (attempt {event.attempt})]")
                    pass
                elif isinstance(event, Reconnected):
                    # print(f"[reconnected; replayed {event.replayed_seconds:.1f}s of audio]")
                    pass
                elif isinstance(event, BufferGap):
                    # print(f"[warning: {event.dropped_seconds:.1f}s of audio lost]")
                    pass

        consumer = asyncio.create_task(consume())
        await feeder
        transcript = await session.flush()
        consumer.cancel()
        print(f"\nfull transcript: {transcript}")


if __name__ == "__main__":
    asyncio.run(main())
