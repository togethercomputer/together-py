from __future__ import annotations

import os
from typing import Any, Callable, Iterable, Iterator, overload
from typing_extensions import Literal, TypeVar

import httpx
import pytest
from respx import MockRouter
from inline_snapshot import external, snapshot, outsource

from together import Together
from together._client import AsyncTogether
from tests.test_utils._utils import print_obj
from together._utils._reflection import assert_signatures_in_sync
from together.lib.streaming.chat import (
    ContentDoneEvent,
    ChatCompletionStream,
    ChatCompletionStreamEvent,
    ChatCompletionStreamManager,
)
from together.types.chat.completion_create_params import Message

from ....conftest import base_url

_T = TypeVar("_T")

# all the snapshots in this file are auto-generated from the live API
#
# you can update them with
#
# `TOGETHER_API_KEY=my_api_key TOGETHER_LIVE=1 rye run pytest tests/lib/streaming/chat/test_completions.py --inline-snapshot=fix`

messages: Iterable[Message] = [
    {
        "role": "user",
        "content": "Say foo and bar and nothing more.",
    },
]


@pytest.mark.respx(base_url=base_url)
def test_final_completion(client: Together, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    listener = _make_stream_snapshot_request(
        lambda c: c.chat.completions.stream(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=messages,
        ),
        content_snapshot=snapshot(external("34d9740d8c13*.bin")),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj(listener.stream.get_final_completion(), monkeypatch) == snapshot(
        """\
ChatCompletion(
    choices=[
        Choice(
            finish_reason='eos',
            index=0,
            logprobs=LogProbs(
                token_ids=[
                    3464,
                    304,
                    2843,
                    28723,
                    315,
                    28742,
                    333,
                    773,
                    767,
                    368,
                    2261,
                    28725,
                    304,
                    1055,
                    315,
                    28742,
                    584,
                    1315,
                    708,
                    680,
                    28723,
                    2
                ],
                token_logprobs=[],
                tokens=[
                    'oo',
                    ' and',
                    ' bar',
                    '.',
                    ' I',
                    "'",
                    've',
                    ' said',
                    ' what',
                    ' you',
                    ' asked',
                    ',',
                    ' and',
                    ' now',
                    ' I',
                    "'",
                    'll',
                    ' say',
                    ' no',
                    ' more',
                    '.',
                    ''
                ]
            ),
            message=ChoiceMessage(
                content=" Foo and bar. I've said what you asked, and now I'll say no more.",
                function_call=None,
                role='assistant',
                token_id=160447,
                tool_calls=None
            ),
            seed=None,
            text=' F'
        )
    ],
    created=1724170981,
    id='8b63b9b7bbf8439d-EWR',
    model='mistralai/Mixtral-8x7B-Instruct-v0.1',
    object='chat.completion',
    system_fingerprint=None,
    usage=ChatCompletionUsage(completion_tokens=23, prompt_tokens=17, total_tokens=40)
)
"""
    )
    assert print_obj(listener.get_event_by_type("content.done"), monkeypatch) == snapshot(
        """\
ContentDoneEvent(content=" Foo and bar. I've said what you asked, and now I'll say no more.", type='content.done')
"""
    )


@pytest.mark.respx(base_url=base_url)
def test_events(client: Together, respx_mock: MockRouter) -> None:
    listener = _make_stream_snapshot_request(
        lambda c: c.chat.completions.stream(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=messages,
        ),
        content_snapshot=snapshot(external("499cb277a2dc*.bin")),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert [e.type for e in listener.events] == snapshot(
        [
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "content.done",
            "logprobs.content.done",
        ]
    )


@pytest.mark.respx(base_url=base_url)
def test_content_logprobs_events(client: Together, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    listener = _make_stream_snapshot_request(
        lambda c: c.chat.completions.stream(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=messages,
            logprobs=True,
        ),
        content_snapshot=snapshot(external("6128ee154265*.bin")),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj([e for e in listener.events if e.type.startswith("logprobs")][-1], monkeypatch) == snapshot("""\
LogprobsContentDoneEvent(type='logprobs.content.done')
""")

    assert print_obj(listener.stream.get_final_completion().choices, monkeypatch) == snapshot("""\
[
    Choice(
        finish_reason='eos',
        index=0,
        logprobs=LogProbs(
            token_ids=[
                3464,
                304,
                2843,
                28723,
                315,
                28742,
                333,
                773,
                767,
                368,
                2261,
                28725,
                304,
                1055,
                315,
                28742,
                584,
                1315,
                708,
                680,
                28723,
                2
            ],
            token_logprobs=[
                -2.3841858e-07,
                -0.011047363,
                -9.536743e-07,
                -4.7683716e-07,
                -0.0234375,
                -0.38671875,
                -0.29492188,
                -3.3140182e-05,
                -3.5762787e-06,
                -5.9843063e-05,
                -0.0053710938,
                -0.35351562,
                -0.58984375,
                -1.5497208e-06,
                -0.13964844,
                -0.00026130676,
                -0.39648438,
                -0.0007095337,
                -3.5762787e-07,
                -4.7683716e-07,
                -5.00679e-06
            ],
            tokens=[
                'oo',
                ' and',
                ' bar',
                '.',
                ' I',
                "'",
                've',
                ' said',
                ' what',
                ' you',
                ' asked',
                ',',
                ' and',
                ' now',
                ' I',
                "'",
                'll',
                ' say',
                ' no',
                ' more',
                '.',
                ''
            ]
        ),
        message=ChoiceMessage(
            content=" Foo and bar. I've said what you asked, and now I'll say no more.",
            function_call=None,
            role='assistant',
            token_id=160447,
            tool_calls=None
        ),
        seed=None,
        text=' F'
    )
]
""")


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_stream_method_in_sync(sync: bool, client: Together, async_client: AsyncTogether) -> None:
    checking_client: Together | AsyncTogether = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.chat.completions.create,
        checking_client.chat.completions.stream,
        exclude_params={"response_format", "stream"},
    )


class StreamListener:
    def __init__(self, stream: ChatCompletionStream) -> None:
        self.stream = stream
        self.events: list[ChatCompletionStreamEvent] = []

    def __iter__(self) -> Iterator[ChatCompletionStreamEvent]:
        for event in self.stream:
            self.events.append(event)
            yield event

    @overload
    def get_event_by_type(self, event_type: Literal["content.done"]) -> ContentDoneEvent | None: ...

    @overload
    def get_event_by_type(self, event_type: str) -> ChatCompletionStreamEvent | None: ...

    def get_event_by_type(self, event_type: str) -> ChatCompletionStreamEvent | None:
        return next((e for e in self.events if e.type == event_type), None)


def _make_stream_snapshot_request(
    func: Callable[[Together], ChatCompletionStreamManager],
    *,
    content_snapshot: Any,
    respx_mock: MockRouter,
    mock_client: Together,
    on_event: Callable[[ChatCompletionStream, ChatCompletionStreamEvent], Any] | None = None,
) -> StreamListener:
    live = os.environ.get("TOGETHER_LIVE") == "1"
    if live:

        def _on_response(response: httpx.Response) -> None:
            # update the content snapshot
            assert outsource(response.read()) == content_snapshot

        respx_mock.stop()

        client = Together(
            http_client=httpx.Client(
                event_hooks={
                    "response": [_on_response],
                }
            )
        )
    else:
        respx_mock.post("/chat/completions").mock(
            return_value=httpx.Response(
                200,
                content=content_snapshot._old_value._load_value(),
                headers={"content-type": "text/event-stream"},
            )
        )

        client = mock_client

    with func(client) as stream:
        listener = StreamListener(stream)

        for event in listener:
            if on_event:
                on_event(stream, event)

    if live:
        client.close()

    return listener
