from typing import Union
from typing_extensions import Literal

from together.types.log_probs import LogProbs

from ._types import ChatCompletionSnapshot
from ...._models import BaseModel, GenericModel
from ....types.chat import ChatCompletionChunk


class ChunkEvent(BaseModel):
    type: Literal["chunk"]

    chunk: ChatCompletionChunk

    snapshot: ChatCompletionSnapshot


class ContentDeltaEvent(BaseModel):
    """This event is yielded for every chunk with `choice.delta.content` data."""

    type: Literal["content.delta"]

    delta: str

    snapshot: str


class ContentDoneEvent(GenericModel):
    type: Literal["content.done"]

    content: str


class FunctionToolCallArgumentsDeltaEvent(BaseModel):
    type: Literal["tool_calls.function.arguments.delta"]

    name: str

    index: float

    arguments: str
    """Accumulated raw JSON string"""

    arguments_delta: str
    """The JSON string delta"""


class FunctionToolCallArgumentsDoneEvent(BaseModel):
    type: Literal["tool_calls.function.arguments.done"]

    name: str

    index: float

    arguments: str
    """Accumulated raw JSON string"""


class LogProbsDeltaEvent(BaseModel):
    type: Literal["logprobs.delta"]

    delta: LogProbs

    snapshot: LogProbs


class LogprobsContentDoneEvent(BaseModel):
    type: Literal["logprobs.content.done"]


ChatCompletionStreamEvent = Union[
    ChunkEvent,
    ContentDeltaEvent,
    ContentDoneEvent,
    FunctionToolCallArgumentsDeltaEvent,
    FunctionToolCallArgumentsDoneEvent,
    LogProbsDeltaEvent,
    LogprobsContentDoneEvent,
]
