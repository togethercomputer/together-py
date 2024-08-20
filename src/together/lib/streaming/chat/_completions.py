from __future__ import annotations

from types import TracebackType
from typing import TYPE_CHECKING, Callable, Awaitable, AsyncIterator, cast
from typing_extensions import Self, Iterator, assert_never

from together.types.log_probs import LogProbs

from ._types import ChoiceSnapshot, ChoiceMessageSnapshot, ChatCompletionSnapshot
from ._events import (
    ChunkEvent,
    ContentDoneEvent,
    ContentDeltaEvent,
    LogProbsDeltaEvent,
    LogprobsContentDoneEvent,
    ChatCompletionStreamEvent,
    FunctionToolCallArgumentsDoneEvent,
    FunctionToolCallArgumentsDeltaEvent,
)
from .._deltas import accumulate_delta
from ...._utils import consume_sync_iterator, consume_async_iterator
from ...._compat import model_dump
from ...._models import build, construct_type
from ...._streaming import Stream, AsyncStream
from ....types.chat import ChatCompletion, ChatCompletionChunk
from ....types.chat.chat_completion_chunk import Choice as ChoiceChunk


class ChatCompletionStream:
    """Wrapper over the Chat Completions streaming API that adds helpful
    events such as `content.done`, supports automatically parsing
    responses & tool calls and accumulates a `ChatCompletion` object
    from each individual chunk.
    """

    def __init__(
        self,
        *,
        raw_stream: Stream[ChatCompletionChunk],
    ) -> None:
        self._raw_stream = raw_stream
        self._response = raw_stream.response
        self._iterator = self.__stream__()
        self._state = ChatCompletionStreamState()

    def __next__(self) -> ChatCompletionStreamEvent:
        return self._iterator.__next__()

    def __iter__(self) -> Iterator[ChatCompletionStreamEvent]:
        for item in self._iterator:
            yield item

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        """
        Close the response and release the connection.

        Automatically called if the response body is read to completion.
        """
        self._response.close()

    def get_final_completion(self) -> ChatCompletion:
        """Waits until the stream has been read to completion and returns
        the accumulated `ChatCompletion` object.
        """
        self.until_done()
        return self._state.get_final_completion()

    def until_done(self) -> Self:
        """Blocks until the stream has been consumed."""
        consume_sync_iterator(self)
        return self

    @property
    def current_completion_snapshot(self) -> ChatCompletionSnapshot:
        return self._state.current_completion_snapshot

    def __stream__(self) -> Iterator[ChatCompletionStreamEvent]:
        for sse_event in self._raw_stream:
            events_to_fire = self._state.handle_chunk(sse_event)
            for event in events_to_fire:
                yield event


class ChatCompletionStreamManager:
    """Context manager over a `ChatCompletionStream` that is returned by `.stream()`.

    This context manager ensures the response cannot be leaked if you don't read
    the stream to completion.

    Usage:
    ```py
    with client.beta.chat.completions.stream(...) as stream:
        for event in stream:
            ...
    ```
    """

    def __init__(
        self,
        api_request: Callable[[], Stream[ChatCompletionChunk]],
    ) -> None:
        self.__stream: ChatCompletionStream | None = None
        self.__api_request = api_request

    def __enter__(self) -> ChatCompletionStream:
        raw_stream = self.__api_request()

        self.__stream = ChatCompletionStream(
            raw_stream=raw_stream,
        )

        return self.__stream

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.__stream is not None:
            self.__stream.close()


class AsyncChatCompletionStream:
    """Wrapper over the Chat Completions streaming API that adds helpful
    events such as `content.done`, supports automatically parsing
    responses & tool calls and accumulates a `ChatCompletion` object
    from each individual chunk.
    """

    def __init__(
        self,
        *,
        raw_stream: AsyncStream[ChatCompletionChunk],
    ) -> None:
        self._raw_stream = raw_stream
        self._response = raw_stream.response
        self._iterator = self.__stream__()
        self._state = ChatCompletionStreamState()

    async def __anext__(self) -> ChatCompletionStreamEvent:
        return await self._iterator.__anext__()

    async def __aiter__(self) -> AsyncIterator[ChatCompletionStreamEvent]:
        async for item in self._iterator:
            yield item

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """
        Close the response and release the connection.

        Automatically called if the response body is read to completion.
        """
        await self._response.aclose()

    async def get_final_completion(self) -> ChatCompletion:
        """Waits until the stream has been read to completion and returns
        the accumulated `ChatCompletion` object.
        """
        await self.until_done()
        return self._state.get_final_completion()

    async def until_done(self) -> Self:
        """Blocks until the stream has been consumed."""
        await consume_async_iterator(self)
        return self

    @property
    def current_completion_snapshot(self) -> ChatCompletionSnapshot:
        return self._state.current_completion_snapshot

    async def __stream__(self) -> AsyncIterator[ChatCompletionStreamEvent]:
        async for sse_event in self._raw_stream:
            events_to_fire = self._state.handle_chunk(sse_event)
            for event in events_to_fire:
                yield event


class AsyncChatCompletionStreamManager:
    """Context manager over a `AsyncChatCompletionStream` that is returned by `.stream()`.

    This context manager ensures the response cannot be leaked if you don't read
    the stream to completion.

    Usage:
    ```py
    async with client.beta.chat.completions.stream(...) as stream:
        for event in stream:
            ...
    ```
    """

    def __init__(
        self,
        api_request: Awaitable[AsyncStream[ChatCompletionChunk]],
    ) -> None:
        self.__stream: AsyncChatCompletionStream | None = None
        self.__api_request = api_request

    async def __aenter__(self) -> AsyncChatCompletionStream:
        raw_stream = await self.__api_request

        self.__stream = AsyncChatCompletionStream(
            raw_stream=raw_stream,
        )

        return self.__stream

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.__stream is not None:
            await self.__stream.close()


class ChatCompletionStreamState:
    def __init__(
        self,
    ) -> None:
        self.__current_completion_snapshot: ChatCompletionSnapshot | None = None
        self.__choice_event_states: list[ChoiceEventState] = []

    def get_final_completion(self) -> ChatCompletion:
        return cast(ChatCompletion, self.__current_completion_snapshot)

    @property
    def current_completion_snapshot(self) -> ChatCompletionSnapshot:
        assert self.__current_completion_snapshot is not None
        return self.__current_completion_snapshot

    def handle_chunk(self, chunk: ChatCompletionChunk) -> list[ChatCompletionStreamEvent]:
        """Accumulate a new chunk into the snapshot and returns a list of events to yield."""
        self.__current_completion_snapshot = self._accumulate_chunk(chunk)

        return self._build_events(
            chunk=chunk,
            completion_snapshot=self.__current_completion_snapshot,
        )

    def _get_choice_state(self, choice: ChoiceChunk) -> ChoiceEventState:
        try:
            return self.__choice_event_states[choice.index]
        except IndexError:
            choice_state = ChoiceEventState()
            self.__choice_event_states.append(choice_state)
            return choice_state

    def _accumulate_chunk(self, chunk: ChatCompletionChunk) -> ChatCompletionSnapshot:
        completion_snapshot = self.__current_completion_snapshot

        if completion_snapshot is None:
            return _convert_initial_chunk_into_snapshot(chunk)

        for choice in chunk.choices:
            try:
                choice_snapshot = completion_snapshot.choices[choice.index]

                if choice_snapshot.message is None:
                    continue

                if choice.finish_reason:
                    choice_snapshot.finish_reason = choice.finish_reason

                choice_snapshot.message = cast(
                    ChoiceMessageSnapshot,
                    construct_type(
                        type_=ChoiceMessageSnapshot,
                        value=accumulate_delta(
                            cast(
                                "dict[object, object]",
                                model_dump(
                                    choice_snapshot.message,
                                ),
                            ),
                            cast("dict[object, object]", choice.delta.to_dict()),
                        ),
                    ),
                )
            except IndexError:
                choice_snapshot = cast(
                    ChoiceSnapshot,
                    construct_type(
                        type_=ChoiceSnapshot,
                        value={
                            **choice.model_dump(exclude_unset=True, exclude={"delta"}),
                            "message": choice.delta.to_dict(),
                        },
                    ),
                )
                completion_snapshot.choices.append(choice_snapshot)

            logprobs = choice_snapshot.logprobs
            if logprobs is None:
                logprobs = build(
                    LogProbs,
                    token_logprobs=[choice.logprobs] if choice.logprobs is not None else [],
                    token_ids=[choice.delta.token_id] if choice.delta.token_id is not None else [],
                    tokens=[choice.delta.content] if choice.delta.content is not None else [],
                )
            else:
                if choice.logprobs is not None and logprobs.token_logprobs is not None:
                    logprobs.token_logprobs.append(choice.logprobs)
                if choice.delta.token_id and logprobs.token_ids is not None:
                    logprobs.token_ids.append(choice.delta.token_id)
                if choice.delta.content is not None and logprobs.tokens is not None:
                    logprobs.tokens.append(choice.delta.content)

        completion_snapshot.usage = chunk.usage

        return completion_snapshot

    def _build_events(
        self,
        *,
        chunk: ChatCompletionChunk,
        completion_snapshot: ChatCompletionSnapshot,
    ) -> list[ChatCompletionStreamEvent]:
        events_to_fire: list[ChatCompletionStreamEvent] = []

        events_to_fire.append(
            build(ChunkEvent, type="chunk", chunk=chunk, snapshot=completion_snapshot),
        )

        for choice in chunk.choices:
            choice_state = self._get_choice_state(choice)
            choice_snapshot = completion_snapshot.choices[choice.index]

            if (
                choice.delta.content is not None
                and choice_snapshot.message is not None
                and choice_snapshot.message.content is not None
            ):
                events_to_fire.append(
                    build(
                        ContentDeltaEvent,
                        type="content.delta",
                        delta=choice.delta.content,
                        snapshot=choice_snapshot.message.content,
                    )
                )

            if choice.delta.tool_calls:
                assert choice_snapshot.message is not None
                tool_calls = choice_snapshot.message.tool_calls
                assert tool_calls is not None

                for tool_call_delta in choice.delta.tool_calls:
                    tool_call = next(tool_call for tool_call in tool_calls if tool_call.index == tool_call_delta.index)

                    if tool_call.type == "function":
                        assert tool_call_delta.function is not None
                        events_to_fire.append(
                            build(
                                FunctionToolCallArgumentsDeltaEvent,
                                type="tool_calls.function.arguments.delta",
                                name=tool_call.function.name,
                                index=tool_call_delta.index,
                                arguments=tool_call.function.arguments,
                                arguments_delta=tool_call_delta.function.arguments or "",
                            )
                        )
                    elif TYPE_CHECKING:  # type: ignore[unreachable]
                        assert_never(tool_call)

            if choice.logprobs and choice_snapshot.logprobs:
                events_to_fire.append(
                    build(
                        LogProbsDeltaEvent,
                        type="logprobs.delta",
                        delta=LogProbs(
                            token_ids=[choice.delta.token_id] if choice.delta.token_id is not None else [],
                            token_logprobs=[choice.logprobs],
                            tokens=[choice.delta.content] if choice.delta.content is not None else [],
                        ),
                        snapshot=choice_snapshot.logprobs,
                    ),
                )

            events_to_fire.extend(
                choice_state.get_done_events(
                    choice_chunk=choice,
                    choice_snapshot=choice_snapshot,
                )
            )

        return events_to_fire


class ChoiceEventState:
    def __init__(self) -> None:
        self._content_done = False
        self._refusal_done = False
        self._logprobs_content_done = False
        self._logprobs_refusal_done = False
        self._done_tool_calls: set[float] = set()
        self.__current_tool_call_index: float | None = None

    def get_done_events(
        self,
        *,
        choice_chunk: ChoiceChunk,
        choice_snapshot: ChoiceSnapshot,
    ) -> list[ChatCompletionStreamEvent]:
        events_to_fire: list[ChatCompletionStreamEvent] = []

        if choice_snapshot.finish_reason:
            events_to_fire.extend(self._content_done_events(choice_snapshot=choice_snapshot))

            if (
                self.__current_tool_call_index is not None
                and self.__current_tool_call_index not in self._done_tool_calls
            ):
                self._add_tool_done_event(
                    events_to_fire=events_to_fire,
                    choice_snapshot=choice_snapshot,
                    tool_index=self.__current_tool_call_index,
                )

        for tool_call in choice_chunk.delta.tool_calls or []:
            if self.__current_tool_call_index != tool_call.index:
                events_to_fire.extend(self._content_done_events(choice_snapshot=choice_snapshot))

                if self.__current_tool_call_index is not None:
                    self._add_tool_done_event(
                        events_to_fire=events_to_fire,
                        choice_snapshot=choice_snapshot,
                        tool_index=self.__current_tool_call_index,
                    )

            self.__current_tool_call_index = tool_call.index

        return events_to_fire

    def _content_done_events(
        self,
        *,
        choice_snapshot: ChoiceSnapshot,
    ) -> list[ChatCompletionStreamEvent]:
        events_to_fire: list[ChatCompletionStreamEvent] = []

        if choice_snapshot.message is not None and choice_snapshot.message.content and not self._content_done:
            self._content_done = True

            events_to_fire.append(
                build(
                    ContentDoneEvent,
                    type="content.done",
                    content=choice_snapshot.message.content,
                ),
            )

        if choice_snapshot.logprobs is not None and not self._logprobs_content_done:
            self._logprobs_content_done = True
            events_to_fire.append(
                build(LogprobsContentDoneEvent, type="logprobs.content.done"),
            )

        return events_to_fire

    def _add_tool_done_event(
        self,
        *,
        events_to_fire: list[ChatCompletionStreamEvent],
        choice_snapshot: ChoiceSnapshot,
        tool_index: float,
    ) -> None:
        if tool_index in self._done_tool_calls:
            return

        self._done_tool_calls.add(tool_index)

        assert choice_snapshot.message is not None
        assert choice_snapshot.message.tool_calls is not None
        tool_call_snapshot = next(
            tool_call for tool_call in choice_snapshot.message.tool_calls if tool_call.index == tool_index
        )

        if tool_call_snapshot.type == "function":
            events_to_fire.append(
                build(
                    FunctionToolCallArgumentsDoneEvent,
                    type="tool_calls.function.arguments.done",
                    index=tool_index,
                    name=tool_call_snapshot.function.name,
                    arguments=tool_call_snapshot.function.arguments,
                )
            )
        elif TYPE_CHECKING:  # type: ignore[unreachable]
            assert_never(tool_call_snapshot)


def _convert_initial_chunk_into_snapshot(chunk: ChatCompletionChunk) -> ChatCompletionSnapshot:
    data = chunk.to_dict()
    choices = cast("list[object]", data["choices"])

    for choice in chunk.choices:
        choices[choice.index] = {
            **choice.model_dump(exclude_unset=True, exclude={"delta"}),
            "message": choice.delta.to_dict(),
            "logprobs": LogProbs(
                token_ids=[],
                token_logprobs=[],
                tokens=[],
            ),
        }

    return cast(
        ChatCompletionSnapshot,
        construct_type(
            type_=ChatCompletionSnapshot,
            value={
                "system_fingerprint": None,
                **data,
                "object": "chat.completion",
            },
        ),
    )
