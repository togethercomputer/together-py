from __future__ import annotations

from typing_extensions import TypeAlias

from together.types.chat.chat_completion import Choice, ChatCompletion

from ....types.chat import ChoiceMessage

ChatCompletionSnapshot: TypeAlias = ChatCompletion
"""Snapshot type representing an in-progress accumulation of
a `ChatCompletion` object.

It is built by accumulating ChatCompletionChunk objects.
"""

ChoiceMessageSnapshot: TypeAlias = ChoiceMessage
"""Snapshot type representing an in-progress accumulation of
a `ChatCompletionMessage` object.

If the content has been fully accumulated, the `.` content will be
the `response_format` instance, otherwise it'll be the raw JSON  version.
"""

ChoiceSnapshot: TypeAlias = Choice
