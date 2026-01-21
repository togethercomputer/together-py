# Manually added to minimize breaking changes from V1
from .tool_choice import ToolChoice
from .chat.chat_completion import ChatCompletion
from .chat.chat_completion_chunk import ChatCompletionChunk as ChatCompletionChunk

ChatCompletionResponse = ChatCompletion
ToolCalls = ToolChoice
