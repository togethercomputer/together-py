from __future__ import annotations

import json

from together.lib.realtime._types import (
    TurnEvent,
    UnknownEvent,
    EchoResponseEvent,
    SessionCreatedEvent,
    TranscriptionDeltaEvent,
    TranscriptionFailedEvent,
    TranscriptionCompletedEvent,
    InputAudioBufferProcessedEvent,
    echo_event,
    append_event,
    commit_event,
    parse_server_event,
    session_update_event,
)


class TestParseServerEvent:
    def test_session_created(self) -> None:
        event = parse_server_event(
            json.dumps(
                {
                    "event_id": "ev1",
                    "type": "session.created",
                    "session": {"id": "s1", "object": "realtime.session", "modalities": ["audio"], "model": "m"},
                }
            )
        )
        assert isinstance(event, SessionCreatedEvent)
        assert event.session is not None
        assert event.session.id == "s1"

    def test_delta_with_timings(self) -> None:
        event = parse_server_event(
            {
                "type": "conversation.item.input_audio_transcription.delta",
                "item_id": "msg_1",
                "delta": "hi",
                "start": 1.5,
                "duration": 0.5,
            }
        )
        assert isinstance(event, TranscriptionDeltaEvent)
        assert event.delta == "hi"
        assert event.start == 1.5

    def test_completed_with_all_fields_absent_except_transcript(self) -> None:
        # Cartesia flush path: no item_id, no start/duration
        event = parse_server_event(
            {"type": "conversation.item.input_audio_transcription.completed", "transcript": "done"}
        )
        assert isinstance(event, TranscriptionCompletedEvent)
        assert event.item_id is None
        assert event.start is None
        assert event.transcript == "done"

    def test_failed_per_turn_vs_fatal(self) -> None:
        per_turn = parse_server_event(
            {
                "type": "conversation.item.input_audio_transcription.failed",
                "item_id": "msg_2",
                "event_type": "completed",
                "error": {"message": "decode blew up"},
            }
        )
        assert isinstance(per_turn, TranscriptionFailedEvent)
        assert per_turn.is_fatal is False

        fatal = parse_server_event(
            {
                "type": "conversation.item.input_audio_transcription.failed",
                "error": {
                    "message": "no",
                    "type": "invalid_request_error",
                    "param": None,
                    "code": "model_not_available",
                },
            }
        )
        assert isinstance(fatal, TranscriptionFailedEvent)
        assert fatal.is_fatal is True
        assert fatal.error is not None
        assert fatal.error.code == "model_not_available"

    def test_turn_events(self) -> None:
        event = parse_server_event(
            {
                "type": "conversation.item.input_audio_transcription.end_of_turn",
                "item_id": "msg_3",
                "transcript": "so far",
                "end_of_turn_confidence": 0.93,
            }
        )
        assert isinstance(event, TurnEvent)
        assert event.end_of_turn_confidence == 0.93

    def test_processed_watermark(self) -> None:
        event = parse_server_event({"type": "input_audio_buffer.processed", "processed_ms": 1234.5})
        assert isinstance(event, InputAudioBufferProcessedEvent)
        assert event.processed_ms == 1234.5

    def test_echo_response(self) -> None:
        event = parse_server_event(
            {"type": "echo.response", "echo_id": 7, "server_received_at": 1.0, "server_sent_at": 2.0}
        )
        assert isinstance(event, EchoResponseEvent)
        assert event.echo_id == 7

    def test_unknown_type_is_forward_compatible(self) -> None:
        event = parse_server_event({"type": "some.future.event", "x": 1})
        assert isinstance(event, UnknownEvent)
        assert event.type == "some.future.event"
        assert event.data == {"type": "some.future.event", "x": 1}

    def test_missing_type_and_non_object(self) -> None:
        assert isinstance(parse_server_event({}), UnknownEvent)
        assert isinstance(parse_server_event(json.dumps([1, 2])), UnknownEvent)

    def test_extra_fields_are_tolerated(self) -> None:
        event = parse_server_event(
            {"type": "conversation.item.input_audio_transcription.delta", "delta": "x", "brand_new_field": {"a": 1}}
        )
        assert isinstance(event, TranscriptionDeltaEvent)


class TestClientEventBuilders:
    def test_append_base64_roundtrip(self) -> None:
        import base64

        event = append_event(b"\x00\x01\x02")
        assert event["type"] == "input_audio_buffer.append"
        assert base64.b64decode(event["audio"]) == b"\x00\x01\x02"

    def test_commit_and_session_update(self) -> None:
        assert commit_event() == {"type": "input_audio_buffer.commit"}
        update = session_update_event({"turn_detection": {"type": "none"}})
        # the server listens for the ".updated" variant
        assert update["type"] == "transcription_session.updated"
        assert update["session"] == {"turn_detection": {"type": "none"}}

    def test_echo(self) -> None:
        assert echo_event() == {"type": "echo"}
        assert echo_event(echo_id=3)["echo_id"] == 3
