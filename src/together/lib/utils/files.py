from __future__ import annotations

import os
import csv
import json
from typing import Any, Dict, List, Union, cast
from pathlib import Path
from traceback import format_exc

from tqdm import tqdm

from together.types import FilePurpose
from together.lib.constants import (
    TOOL_ROLE,
    USER_ROLE,
    MIN_SAMPLES,
    DISABLE_TQDM,
    ASSISTANT_ROLE,
    MAX_IMAGE_BYTES,
    NUM_BYTES_IN_GB,
    MAX_FILE_SIZE_GB,
    MAX_IMAGES_PER_EXAMPLE,
    MAX_BASE64_IMAGE_LENGTH,
    PARQUET_EXPECTED_COLUMNS,
    POSSIBLE_MESSAGE_COLUMNS,
    JSONL_REQUIRED_COLUMNS_MAP,
    POSSIBLE_ROLES_CONVERSATION,
    DatasetFormat,
)

# MessageContent is a string or a list of dicts with 'type': 'text' or 'image_url', and 'text' or 'image_url.url'
# Example: "Hello" or [
#   {"type": "text", "text": "Hello"},
#   {"type": "image_url", "image_url": {
#     "url": "data:image/jpeg;base64,..."
#   }}
# ]
MessageContent = Union[str, List[Dict[str, Any]]]


class InvalidFileFormatError(ValueError):
    """Exception raised for invalid file formats during file checks."""

    def __init__(
        self,
        message: str = "",
        line_number: int | None = None,
        error_source: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.line_number = line_number
        self.error_source = error_source


def check_file(
    file: Path | str,
    purpose: FilePurpose | str = "fine-tune",
) -> Dict[str, Any]:
    if not isinstance(file, Path):
        file = Path(file)

    report_dict: Dict[str, Any] = {
        "is_check_passed": True,
        "message": "Checks passed",
        "found": None,
        "file_size": None,
        "utf8": None,
        "line_type": None,
        "text_field": None,
        "key_value": None,
        "has_min_samples": None,
        "num_samples": None,
        "load_json": None,
        "load_csv": None,
    }

    if not file.is_file():
        report_dict["found"] = False
        report_dict["is_check_passed"] = False
        return report_dict
    else:
        report_dict["found"] = True

    file_size = os.stat(file.as_posix()).st_size

    if file_size > MAX_FILE_SIZE_GB * NUM_BYTES_IN_GB:
        report_dict["message"] = (
            f"Maximum supported file size is {MAX_FILE_SIZE_GB} GB. Found file with size of {round(file_size / NUM_BYTES_IN_GB, 3)} GB."
        )
        report_dict["is_check_passed"] = False
    elif file_size == 0:
        report_dict["message"] = "File is empty"
        report_dict["file_size"] = 0
        report_dict["is_check_passed"] = False
        return report_dict
    else:
        report_dict["file_size"] = file_size

    data_report_dict = {}
    if file.suffix == ".jsonl":
        report_dict["filetype"] = "jsonl"
        data_report_dict = _check_jsonl(file, purpose)
    elif file.suffix == ".parquet":
        report_dict["filetype"] = "parquet"
        data_report_dict = _check_parquet(file, purpose)
    elif file.suffix == ".csv":
        report_dict["filetype"] = "csv"
        data_report_dict = _check_csv(file, purpose)
    else:
        report_dict["filetype"] = (
            f"Unknown extension of file {file}. Only files with extensions .jsonl, .parquet, and .csv are supported."
        )
        report_dict["is_check_passed"] = False

    report_dict.update(data_report_dict)

    return report_dict


def _check_conversation_message_structure(
    message: Dict[str, Any],
    idx: int,
) -> None:
    """Check that the message has correct structure.

    Args:
        message: The message to check.
        idx: Line number in the file.

    Raises:
        InvalidFileFormatError: If the message structure is invalid.
    """
    for column, (required, column_type, column_type_str) in POSSIBLE_MESSAGE_COLUMNS.items():
        if column not in message:
            if not required:
                continue
            raise InvalidFileFormatError(
                message=f"Missing required column `{column}` in message on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )

        if not isinstance(message[column], column_type):
            raise InvalidFileFormatError(
                message=f"Column `{column}` is not {column_type_str} on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )


def _check_message_weight(message: Dict[str, Any], idx: int) -> int | None:
    """Check that the message has a weight with the correct type and value.

    Args:
        message: The message to check.
        idx: Line number in the file.

    Returns:
        int | None: The weight if present, None otherwise.

    Raises:
        InvalidFileFormatError: If the message weight is invalid.
    """
    if "weight" in message:
        weight = message["weight"]
        if weight not in {0, 1}:
            raise InvalidFileFormatError(
                message=f"Weight must be either 0 or 1 on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )
        return weight

    return None


def _check_message_role(message: Dict[str, Any], idx: int) -> str:
    """Check that the message has a valid role.

    Args:
        message: The message to check.
        idx: Line number in the file.

    Returns:
        str: The role of the current message.

    Raises:
        InvalidFileFormatError: If the message role is invalid.
    """
    if message["role"] not in POSSIBLE_ROLES_CONVERSATION:
        raise InvalidFileFormatError(
            message=f"Invalid role `{message['role']}` in conversation on line {idx + 1}. "
            f"Possible roles: {', '.join(POSSIBLE_ROLES_CONVERSATION)}",
            line_number=idx + 1,
            error_source="key_value",
        )
    return message["role"]


def _validate_message_body_requirements(message: Dict[str, Any], idx: int) -> None:
    """Validate that message has appropriate body based on role.

    Args:
        message: The message to validate.
        idx: Line number in the file.

    Raises:
        InvalidFileFormatError: If the message body doesn't meet role requirements.
    """
    role = message["role"]
    has_content = "content" in message and message["content"] is not None
    has_tool_calls = "tool_calls" in message and message["tool_calls"] is not None

    if role == ASSISTANT_ROLE:
        if not has_content and not has_tool_calls:
            raise InvalidFileFormatError(
                message=f"Assistant message must have 'content' and/or 'tool_calls' on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )
    else:
        if not has_content:
            raise InvalidFileFormatError(
                message=f"Message with role '{role}' must have 'content' on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )
        if has_tool_calls:
            raise InvalidFileFormatError(
                message=f"Message with role '{role}' cannot have 'tool_calls' on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )


def _validate_tool_calls(tool_calls: List[Dict[str, Any]], tools: List[Dict[str, Any]] | None, idx: int) -> None:
    """Validate the tool_calls structure.

    Args:
        tool_calls: The list of tool calls to validate.
        tools: The tools available in the conversation, if provided.
        idx: Line number in the file.

    Raises:
        InvalidFileFormatError: If the tool_calls structure is invalid.
    """

    tool_names = None
    if tools is not None:
        tool_names = [tool["function"]["name"] for tool in tools]

    for tool_call in tool_calls:
        if "type" not in tool_call:
            raise InvalidFileFormatError(
                message=f"Each tool call must have a 'type' field on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )

        if tool_call["type"] == "function":
            if "function" not in tool_call:
                raise InvalidFileFormatError(
                    message=f"Tool call with type 'function' must have a 'function' field on line {idx + 1}.",
                    line_number=idx + 1,
                    error_source="key_value",
                )

            if not isinstance(tool_call["function"], dict):
                raise InvalidFileFormatError(
                    message=f"'tool_call.function' must be a dictionary on line {idx + 1}.",
                    line_number=idx + 1,
                    error_source="key_value",
                )

            if "name" not in tool_call["function"]:
                raise InvalidFileFormatError(
                    message=f"Each tool call function must have a 'name' field on line {idx + 1}.",
                    line_number=idx + 1,
                    error_source="key_value",
                )

            if not isinstance(tool_call["function"]["name"], str):
                raise InvalidFileFormatError(
                    message=f"'tool_call.function.name' must be a string on line {idx + 1}.",
                    line_number=idx + 1,
                    error_source="key_value",
                )

            if tool_names is not None and tool_call["function"]["name"] not in tool_names:
                raise InvalidFileFormatError(
                    message=f"'tool_call.function.name' must reference a tool in the tools list on line {idx + 1}. "
                    f"Got '{tool_call['function']['name']}' but available tools are: {', '.join(tool_names)}",
                    line_number=idx + 1,
                    error_source="key_value",
                )

            if "arguments" in tool_call["function"]:
                if not isinstance(tool_call["function"]["arguments"], str):
                    raise InvalidFileFormatError(
                        message=f"'tool_call.function.arguments' must be a serialized JSON string on line {idx + 1}.",
                        line_number=idx + 1,
                        error_source="key_value",
                    )

                try:
                    arguments = json.loads(tool_call["function"]["arguments"])
                except json.JSONDecodeError:
                    raise InvalidFileFormatError(
                        message=f"'tool_call.function.arguments' must be valid JSON on line {idx + 1}.",
                        line_number=idx + 1,
                        error_source="key_value",
                    ) from None

                if not isinstance(arguments, dict):
                    raise InvalidFileFormatError(
                        message=f"'tool_call.function.arguments' must deserialize to an object on line {idx + 1}.",
                        line_number=idx + 1,
                        error_source="key_value",
                    )


def _validate_tools(tools: List[Dict[str, Any]], idx: int) -> None:
    """Validate the tools structure in an example.

    Args:
        tools: The tools to validate.
        idx: Line number in the file.

    Raises:
        InvalidFileFormatError: If the tools structure is malformed.
    """

    if len(tools) == 0:
        raise InvalidFileFormatError(
            message=f"'tools' must not be empty if provided on line {idx + 1}.",
            line_number=idx + 1,
            error_source="key_value",
        )

    for tool in tools:
        if "type" not in tool:
            raise InvalidFileFormatError(
                message=f"Each tool must have a 'type' field on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )

        if tool["type"] != "function":
            raise InvalidFileFormatError(
                message=f"Tool type must be 'function', got '{tool['type']}' on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )

        if "function" not in tool:
            raise InvalidFileFormatError(
                message=f"Each tool must have a 'function' field on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )

        if not isinstance(tool["function"], dict):
            raise InvalidFileFormatError(
                message=f"'function' must be a dictionary on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )

        if "name" not in tool["function"]:
            raise InvalidFileFormatError(
                message=f"Each function must have a 'name' field on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )

        if not isinstance(tool["function"]["name"], str):
            raise InvalidFileFormatError(
                message=f"Function 'name' must be a string on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )


def _validate_content(
    content: MessageContent,
    role: str,
    weight: int | None,
    idx: int,
) -> tuple[bool, int]:
    """Validate message content and return image count.

    Args:
        content: The content of the message.
        role: The role of the message.
        weight: The weight of the message, if provided.
        idx: Line number in the file.

    Returns:
        tuple[bool, int]: Whether the message is multimodal and the number of images in the message.
    """
    images_allowed = role == USER_ROLE

    # Handle text content
    if isinstance(content, str):
        return False, 0

    # Handle multimodal content (content must be List[Dict[str, Any]] at this point)
    num_images = _parse_multimodal_content(content, images_allowed, idx)

    if num_images > 0 and weight is not None and weight != 0:
        raise InvalidFileFormatError(
            message=f"Messages with images cannot have non-zero weights on line {idx + 1}.",
            line_number=idx + 1,
            error_source="key_value",
        )

    return True, num_images


def _parse_multimodal_content(content: List[Any], images_allowed: bool, idx: int) -> int:
    """Parse and validate multimodal content list.

    Args:
        content: List of content items (text and/or images).
        images_allowed: Whether images are allowed in this content.
        idx: Line number in the file.

    Returns:
        int: The number of images found.
    """
    num_images = 0

    for item in content:
        if not isinstance(item, dict):
            raise InvalidFileFormatError(
                message=f"The `content` field must be a list of dicts on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )

        if "type" not in item:
            raise InvalidFileFormatError(
                message=f"The `content` items must have a `type` field on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )

        if item["type"] == "text":
            if "text" not in item or not isinstance(item["text"], str):
                raise InvalidFileFormatError(
                    message=f"The `text` field must be present and be a string on line {idx + 1}. ",
                    line_number=idx + 1,
                    error_source="key_value",
                )
        elif item["type"] == "image_url":
            if not images_allowed:
                raise InvalidFileFormatError(
                    message=f"Only user messages can contain images on line {idx + 1}.",
                    line_number=idx + 1,
                    error_source="key_value",
                )
            _validate_image_data(item, idx)  # type: ignore[reportUnknownArgumentType]
            num_images += 1
        else:
            raise InvalidFileFormatError(
                message=f"The `type` field must be 'text' or 'image_url' on line {idx + 1}. Got {item['type']!r}.",
                line_number=idx + 1,
                error_source="key_value",
            )

    if num_images > MAX_IMAGES_PER_EXAMPLE:
        raise InvalidFileFormatError(
            message=f"The `content` field must contain at most {MAX_IMAGES_PER_EXAMPLE} images on line {idx + 1}, "
            f"found {num_images}.",
            line_number=idx + 1,
            error_source="key_value",
        )

    return num_images


def _validate_image_data(item: Dict[str, Any], idx: int) -> None:
    """Validate the image data.

    Args:
        item: The content item containing image_url.
        idx: Line number in the file.
    """
    image_url_dict: Dict[str, Any] | None = item.get("image_url")
    if not image_url_dict or not isinstance(image_url_dict.get("url"), str):
        raise InvalidFileFormatError(
            message=f"The `image_url` field must be a dictionary with a `url` string on line {idx + 1}. "
            f"Got {image_url_dict!r} instead.",
            line_number=idx + 1,
            error_source="key_value",
        )
    image_data: str = image_url_dict["url"]

    if not any(image_data.startswith(f"data:image/{fmt};base64,") for fmt in ["jpeg", "png", "webp"]):
        raise InvalidFileFormatError(
            message=f"The `url` field must be a JPEG, PNG or WEBP base64-encoded image on line {idx + 1}. "
            f"Got '{image_data[:100]}...' instead.",
            line_number=idx + 1,
            error_source="key_value",
        )

    if len(image_data) > MAX_BASE64_IMAGE_LENGTH:
        raise InvalidFileFormatError(
            message=f"The image must be less than {MAX_IMAGE_BYTES // (1024**2)}MB on line {idx + 1}, "
            f"found ~{len(image_data) * 3 // 4} bytes.",
            line_number=idx + 1,
            error_source="key_value",
        )


def validate_message(
    message: Dict[str, Any],
    tools: List[Dict[str, Any]] | None,
    idx: int,
) -> tuple[str, int | None, bool, int, bool]:
    """Validate a single message through a clear pipeline.

    Args:
        message: The message to validate.
        tools: The tools in the conversation, if provided.
        idx: Line number in the file.

    Returns:
        tuple[str, int | None, bool, int, bool]: The role, weight, whether the message is multimodal,
        the number of images, and whether tools are used in this message.
    """
    is_multimodal = False
    has_tools = False

    _check_conversation_message_structure(message, idx)

    role = _check_message_role(message, idx)
    weight = _check_message_weight(message, idx)

    _validate_message_body_requirements(message, idx)

    if role == TOOL_ROLE:
        has_tools = True

    num_images = 0
    content = message.get("content")
    if content is not None:
        is_multimodal, num_images = _validate_content(content, role, weight, idx)

    tool_calls = message.get("tool_calls")
    if tool_calls is not None:
        _validate_tool_calls(tool_calls, tools, idx)
        has_tools = True

    return role, weight, is_multimodal, num_images, has_tools


def _update_dataset_multimodality(
    dataset_is_multimodal: bool | None,
    example_is_multimodal: bool,
    idx: int,
) -> bool:
    """Update and validate dataset multimodality consistency.

    Args:
        dataset_is_multimodal: Current multimodality state (None if not yet determined).
        example_is_multimodal: Whether the current example is multimodal.
        idx: Line number in the file.

    Returns:
        bool: The updated multimodality state.

    Raises:
        InvalidFileFormatError: If multimodality is inconsistent.
    """
    if dataset_is_multimodal is None:
        return example_is_multimodal
    if dataset_is_multimodal != example_is_multimodal:
        raise InvalidFileFormatError(
            message=f"Cannot mix text-only and multimodal messages in the same dataset on line {idx + 1}.",
            line_number=idx + 1,
            error_source="key_value",
        )
    return dataset_is_multimodal


def validate_messages(
    messages: List[Dict[str, Any]],
    idx: int,
    tools: List[Dict[str, Any]] | None = None,
    require_assistant_role: bool = True,
) -> tuple[bool, bool, bool]:
    """Validate the messages column.

    Args:
        messages: List of message dictionaries to validate.
        idx: Line number in the file.
        tools: The tools in the conversation, if provided.
        require_assistant_role: Whether to require at least one assistant role.

    Returns:
        tuple[bool, bool, bool]: Whether weights are present, whether the messages are multimodal,
        and whether the messages have tools.

    Raises:
        InvalidFileFormatError: If the messages are invalid.
    """
    if len(messages) == 0:
        raise InvalidFileFormatError(
            message=f"The `messages` column must not be empty on line {idx + 1}.",
            line_number=idx + 1,
            error_source="key_value",
        )

    messages_have_weights = False
    messages_have_tools = False
    assistant_role_exists = False
    total_number_of_images = 0
    conversation_is_multimodal: bool | None = None

    for message in messages:
        message = {k: v for k, v in message.items() if v is not None}
        message_role, message_weight, message_is_multimodal, message_number_of_images, message_has_tools = (
            validate_message(message, tools, idx)
        )
        messages_have_weights |= message_weight is not None
        messages_have_tools |= message_has_tools
        assistant_role_exists |= message_role == ASSISTANT_ROLE
        conversation_is_multimodal = _update_dataset_multimodality(
            conversation_is_multimodal, message_is_multimodal, idx
        )
        total_number_of_images += message_number_of_images

    if conversation_is_multimodal and total_number_of_images == 0:
        raise InvalidFileFormatError(
            message=f"The `messages` must contain at least one image if it is multimodal on line {idx + 1}.",
            line_number=idx + 1,
            error_source="key_value",
        )
    if total_number_of_images > MAX_IMAGES_PER_EXAMPLE:
        raise InvalidFileFormatError(
            message=f"The `messages` must contain at most {MAX_IMAGES_PER_EXAMPLE} images on line {idx + 1}. "
            f"Found {total_number_of_images} images.",
            line_number=idx + 1,
            error_source="key_value",
        )
    if require_assistant_role and not assistant_role_exists:
        raise InvalidFileFormatError(
            message=f"At least one message with the assistant role must be present on line {idx + 1}.",
            line_number=idx + 1,
            error_source="key_value",
        )

    return messages_have_weights, conversation_is_multimodal or False, messages_have_tools


def validate_preference_openai(example: Dict[str, Any], idx: int = 0) -> tuple[bool, bool]:
    """Validate the OpenAI preference dataset format.

    Args:
        example: Input entry to be checked.
        idx: Line number in the file.

    Returns:
        tuple[bool, bool]: Whether the messages are multimodal and whether the messages have tools.

    Raises:
        InvalidFileFormatError: If the dataset format is invalid.
    """
    if not isinstance(example["input"], dict):
        raise InvalidFileFormatError(
            message=f"The `input` field must be a dictionary on line {idx + 1}.",
            line_number=idx + 1,
            error_source="key_value",
        )

    if "messages" not in example["input"]:
        raise InvalidFileFormatError(
            message=f"The `input` dictionary must contain a `messages` field on line {idx + 1}.",
            line_number=idx + 1,
            error_source="key_value",
        )

    # TODO: Support tools in preference openai format
    messages = cast(List[Dict[str, dict[str, Any]]], example["input"]["messages"])
    _, is_multimodal, has_tools = validate_messages(messages, idx, tools=None, require_assistant_role=False)

    if example["input"]["messages"][-1]["role"] == "assistant":
        raise InvalidFileFormatError(
            message=f"The last message in the input conversation must not be from the assistant on line {idx + 1}.",
            line_number=idx + 1,
            error_source="key_value",
        )

    keys = ["preferred_output", "non_preferred_output"]

    for key in keys:
        if key not in example:
            raise InvalidFileFormatError(
                message=f"The dataset is malformed, the `{key}` field must be present in the input dictionary on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )

        if not isinstance(example[key], list):
            raise InvalidFileFormatError(
                message=f"The dataset is malformed, the `{key}` field must be a list on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )

        if len(example[key]) != 1:
            raise InvalidFileFormatError(
                message=f"The dataset is malformed, the `{key}` list must contain exactly one message on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )

        message = example[key][0]

        if not isinstance(message, dict):
            raise InvalidFileFormatError(
                message=f"The first element of `{key}` must be a dictionary on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )

        _check_conversation_message_structure(message, idx)  # type: ignore[reportUnknownArgumentType]

        if message["role"] != "assistant":
            raise InvalidFileFormatError(
                message=f"The first element of `{key}` must have the 'assistant' role on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )

        if "content" not in message:
            raise InvalidFileFormatError(
                message=f"The first element of `{key}` must have a 'content' field on line {idx + 1}.",
                line_number=idx + 1,
                error_source="key_value",
            )

        message_is_multimodal, _ = _validate_content(
            content=message["content"],  # type: ignore[reportUnknownArgumentType]
            role=message["role"],
            weight=None,
            idx=idx,
        )
        is_multimodal = _update_dataset_multimodality(is_multimodal, message_is_multimodal, idx)

    return is_multimodal, has_tools


def _check_utf8(file: Path) -> Dict[str, Any]:
    """Check if the file is UTF-8 encoded.

    Args:
        file (Path): Path to the file to check.
    Returns:
        Dict[str, Any]: A dictionary with the results of the check.
    """
    report_dict: Dict[str, Any] = {}
    try:
        # Dry-run UTF-8 decode by iterating through the file to avoid loading it entirely into memory
        with file.open(encoding="utf-8") as f:
            for _ in f:
                pass
        report_dict["utf8"] = True
    except UnicodeDecodeError as e:
        report_dict["utf8"] = False
        report_dict["message"] = f"File is not UTF-8 encoded. Error raised: {e}."
        report_dict["is_check_passed"] = False
    return report_dict


def _check_samples_count(file: Path, report_dict: Dict[str, Any], idx: int) -> Dict[str, Any]:
    if idx + 1 < MIN_SAMPLES:
        report_dict["has_min_samples"] = False
        report_dict["message"] = (
            f"Processing {file} resulted in only {idx + 1} samples. Our minimum is {MIN_SAMPLES} samples. "
        )
        report_dict["is_check_passed"] = False
    else:
        report_dict["num_samples"] = idx + 1
        report_dict["has_min_samples"] = True

    return report_dict


def _check_csv(file: Path, purpose: FilePurpose | str) -> Dict[str, Any]:
    """Check if the file is a valid CSV file.

    Args:
        file (Path): Path to the file to check.
        purpose (FilePurpose | str): Purpose of the file, used to determine if the file should be checked for specific columns.

    Returns:
        Dict[str, Any]: A dictionary with the results of the check.
    """
    report_dict: Dict[str, Any] = {}
    if purpose != "eval":
        report_dict["is_check_passed"] = False
        report_dict["message"] = (
            f"CSV files are not supported for {purpose}. Only JSONL and Parquet files are supported."
        )
        return report_dict

    report_dict.update(_check_utf8(file))

    if not report_dict["utf8"]:
        return report_dict

    with file.open() as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            report_dict["message"] = "CSV file is empty or has no header."
            report_dict["is_check_passed"] = False
            return report_dict
        idx = -1

        try:
            # for loop to iterate through the CSV rows
            for idx, item in enumerate(reader):
                if None in item.keys() or None in item.values():
                    raise InvalidFileFormatError(
                        message=f"CSV file is malformed or the number of columns found on line {idx + 1} is inconsistent with the header",
                        line_number=idx + 1,
                        error_source="format",
                    )

            report_dict.update(_check_samples_count(file, report_dict, idx))
            report_dict["load_csv"] = True

        except InvalidFileFormatError as e:
            report_dict["load_csv"] = False
            report_dict["is_check_passed"] = False
            report_dict["message"] = e.message
            if e.line_number is not None:
                report_dict["line_number"] = e.line_number
            if e.error_source is not None:
                report_dict[e.error_source] = False
        except ValueError:
            report_dict["load_csv"] = False
            if idx < 0:
                report_dict["message"] = "Unable to decode file. File may be empty or in an unsupported format. "
            else:
                report_dict["message"] = f"Error parsing the CSV file. Unexpected format on line {idx + 1}."
            report_dict["is_check_passed"] = False

    return report_dict


def _check_jsonl(file: Path, purpose: FilePurpose | str) -> Dict[str, Any]:
    report_dict: Dict[str, Any] = {}
    report_dict.update(_check_utf8(file))
    if not report_dict["utf8"]:
        return report_dict

    dataset_format = None
    with file.open() as f:
        idx = -1
        try:
            for idx, line in tqdm(
                enumerate(f),
                desc="Validating file",
                unit=" lines",
                disable=bool(DISABLE_TQDM),
            ):
                json_line = json.loads(line)

                if not isinstance(json_line, dict):
                    raise InvalidFileFormatError(
                        message=(
                            f"Error parsing file. Invalid format on line {idx + 1} of the input file. "
                            "Datasets must follow text, conversational, or instruction format. For more"
                            "information, see https://docs.together.ai/docs/fine-tuning-data-preparation"
                        ),
                        line_number=idx + 1,
                        error_source="line_type",
                    )
                # In evals, we don't check the format of the dataset.
                if purpose != "eval":
                    current_format = None
                    for possible_format in JSONL_REQUIRED_COLUMNS_MAP:
                        if all(column in json_line for column in JSONL_REQUIRED_COLUMNS_MAP[possible_format]):
                            if current_format is None:
                                current_format = possible_format
                            elif current_format != possible_format:  # type: ignore[unreachable]
                                raise InvalidFileFormatError(
                                    message="Found multiple dataset formats in the input file. "
                                    f"Got {current_format} and {possible_format} on line {idx + 1}.",
                                    line_number=idx + 1,
                                    error_source="format",
                                )

                            # Check that there are no extra columns
                            # Allow 'tools' column for conversation format
                            allowed_extra: set[str] = (
                                {"tools"} if possible_format == DatasetFormat.CONVERSATION else set()
                            )
                            for column in cast(List[str], json_line.keys()):
                                if (
                                    column not in JSONL_REQUIRED_COLUMNS_MAP[possible_format]
                                    and column not in allowed_extra
                                ):
                                    raise InvalidFileFormatError(
                                        message=f'Found extra column "{column}" in the line {idx + 1}.',
                                        line_number=idx + 1,
                                        error_source="format",
                                    )

                    if current_format is None:
                        raise InvalidFileFormatError(
                            message=(
                                f"Error parsing file. Could not detect a format for the line {idx + 1} with the columns:\n"
                                f"{json_line.keys()}"
                            ),
                            line_number=idx + 1,
                            error_source="format",
                        )

                    if current_format == DatasetFormat.PREFERENCE_OPENAI:
                        validate_preference_openai(json_line, idx)  # type: ignore[reportUnknownArgumentType]
                    elif current_format == DatasetFormat.PREFERENCE:
                        for column in JSONL_REQUIRED_COLUMNS_MAP[current_format]:
                            column_value = json_line[column]  # type: ignore[reportUnknownVariableType]
                            if not isinstance(column_value, list):
                                raise InvalidFileFormatError(
                                    message=f"The column `{column}` must be a list on line {idx + 1}.",
                                    line_number=idx + 1,
                                    error_source="key_value",
                                )
                            if len(column_value) == 0:  # type: ignore[reportUnknownArgumentType]
                                raise InvalidFileFormatError(
                                    message=f"The column `{column}` must not be empty on line {idx + 1}.",
                                    line_number=idx + 1,
                                    error_source="key_value",
                                )
                            validate_messages(column_value, idx)  # type: ignore[reportUnknownArgumentType]
                            if column_value[-1].get("role") != "assistant":  # type: ignore[reportUnknownMemberType]
                                raise InvalidFileFormatError(
                                    message=f"The last message in `{column}` must be from an assistant on line {idx + 1}.",
                                    line_number=idx + 1,
                                    error_source="key_value",
                                )
                    elif current_format == DatasetFormat.CONVERSATION:
                        # Validate tools if present
                        tools = json_line.get("tools")  # type: ignore[reportUnknownVariableType, reportUnknownMemberType]
                        if tools is not None:
                            _validate_tools(tools, idx)  # type: ignore[reportUnknownArgumentType]

                        message_column = JSONL_REQUIRED_COLUMNS_MAP[DatasetFormat.CONVERSATION][0]
                        require_assistant = purpose != "eval"
                        messages = json_line[message_column]  # type: ignore[reportUnknownVariableType]
                        validate_messages(
                            messages,  # type: ignore[reportUnknownArgumentType]
                            idx,
                            tools=tools,  # type: ignore[reportUnknownArgumentType]
                            require_assistant_role=require_assistant,
                        )
                    else:  # GENERAL, INSTRUCTION formats
                        for column in JSONL_REQUIRED_COLUMNS_MAP[current_format]:
                            role = ASSISTANT_ROLE if column in {"completion"} else USER_ROLE
                            _validate_content(json_line[column], role=role, weight=None, idx=idx)  # type: ignore[reportUnknownArgumentType]

                    if dataset_format is None:
                        dataset_format = current_format
                    elif current_format != dataset_format:  # type: ignore[unreachable]
                        raise InvalidFileFormatError(
                            message="All samples in the dataset must have the same dataset format. "
                            f"Got {dataset_format} for the first line and {current_format} "
                            f"for the line {idx + 1}.",
                            line_number=idx + 1,
                            error_source="format",
                        )
            report_dict.update(_check_samples_count(file, report_dict, idx))

            report_dict["load_json"] = True

        except InvalidFileFormatError as e:
            report_dict["load_json"] = False
            report_dict["is_check_passed"] = False
            report_dict["message"] = e.message
            if e.line_number is not None:
                report_dict["line_number"] = e.line_number
            if e.error_source is not None:
                report_dict[e.error_source] = False
        except ValueError:
            report_dict["load_json"] = False
            if idx < 0:
                report_dict["message"] = "Unable to decode file. File may be empty or in an unsupported format. "
            else:
                report_dict["message"] = f"Error parsing json payload. Unexpected format on line {idx + 1}."
            report_dict["is_check_passed"] = False

    if "text_field" not in report_dict:
        report_dict["text_field"] = True
    if "line_type" not in report_dict:
        report_dict["line_type"] = True
    if "key_value" not in report_dict:
        report_dict["key_value"] = True
    return report_dict


def _check_parquet(file: Path, purpose: FilePurpose | str) -> Dict[str, Any]:
    try:
        # Pyarrow is optional as it's large (~80MB) and isn't compatible with older systems.
        from pyarrow import ArrowInvalid, parquet  # type: ignore[reportMissingTypeStubs, reportUnknownVariableType]
    except ImportError as e:
        raise ImportError(
            "pyarrow is not installed and is required to use parquet files. Please install it via `pip install together[pyarrow]`"
        ) from e

    report_dict: Dict[str, Any] = {}
    if purpose == "eval":
        report_dict["is_check_passed"] = False
        report_dict["message"] = (
            f"Parquet files are not supported for {purpose}. Only JSONL and CSV files are supported."
        )
        return report_dict

    try:
        table = parquet.read_table(str(file), memory_map=True)  # type: ignore[reportUnknownMemberType]
    except ArrowInvalid:
        report_dict["load_parquet"] = (
            f"An exception has occurred when loading the Parquet file {file}. Please check the file for corruption. "
            f"Exception trace:\n{format_exc()}"
        )
        report_dict["is_check_passed"] = False
        return report_dict

    column_names = table.schema.names  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
    if "input_ids" not in column_names:
        report_dict["load_parquet"] = f"Parquet file {file} does not contain the `input_ids` column."
        report_dict["is_check_passed"] = False
        return report_dict

    # Don't check for eval
    for column_name in column_names:  # type: ignore[reportUnknownVariableType]
        if column_name not in PARQUET_EXPECTED_COLUMNS:
            report_dict["load_parquet"] = (
                f"Parquet file {file} contains an unexpected column {column_name}. "
                f"Only columns {PARQUET_EXPECTED_COLUMNS} are supported."
            )
            report_dict["is_check_passed"] = False
            return report_dict

    num_samples = len(table)  # type: ignore[reportUnknownArgumentType]
    if num_samples < MIN_SAMPLES:
        report_dict["has_min_samples"] = False
        report_dict["message"] = (
            f"Processing {file} resulted in only {num_samples} samples. Our minimum is {MIN_SAMPLES} samples. "
        )
        report_dict["is_check_passed"] = False
        return report_dict
    else:
        report_dict["num_samples"] = num_samples

    report_dict["is_check_passed"] = True

    return report_dict
