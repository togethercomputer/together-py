from together.types.chat.completion_create_params import (
    MessageChatCompletionUserMessageParam,
    ChatCompletionStructuredMessageTextParam,
    ChatCompletionStructuredMessageVideoURLParam,
)
from together.types.chat.chat_completion_structured_message_video_url_param import VideoURL


def test_video_url_message():
    # Test creating a message with video_url content
    message = MessageChatCompletionUserMessageParam(
        role="user",
        content=[
            ChatCompletionStructuredMessageTextParam(type="text", text="What's in this video?"),
            ChatCompletionStructuredMessageVideoURLParam(
                type="video_url",
                video_url=VideoURL(url="https://example.com/video.mp4"),
            ),
        ],
    )

    # Verify the message structure
    assert message["role"] == "user"
    assert isinstance(message["content"], list)
    assert len(message["content"]) == 2

    # Verify text content
    assert "type" in message["content"][0]
    assert message["content"][0]["type"] == "text"
    assert message["content"][0]["text"] == "What's in this video?"

    # Verify video_url content
    assert "type" in message["content"][1]
    assert message["content"][1]["type"] == "video_url"
    assert message["content"][1]["video_url"]["url"] == "https://example.com/video.mp4"
