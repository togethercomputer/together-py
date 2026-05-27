import csv
import json
from typing import Any, Dict, List, cast
from pathlib import Path

import pytest

from together.lib.utils.files import check_file


def test_check_jsonl_valid_general(tmp_path: Path):
    # Create a valid JSONL file
    file = tmp_path / "valid.jsonl"
    content = [{"text": "Hello, world!"}, {"text": "How are you?"}]
    with file.open("w") as f:
        f.write("\n".join(json.dumps(item) for item in content))

    report = check_file(file)

    assert report["is_check_passed"]
    assert report["utf8"]
    assert report["num_samples"] == len(content)
    assert report["has_min_samples"]


def test_check_jsonl_valid_instruction(tmp_path: Path):
    # Create a valid JSONL file with instruction format
    file = tmp_path / "valid_instruction.jsonl"
    content = [
        {"prompt": "Translate the following sentence.", "completion": "Hello, world!"},
        {
            "prompt": "Summarize the text.",
            "completion": "Weyland-Yutani Corporation creates advanced AI.",
        },
    ]
    with file.open("w") as f:
        f.write("\n".join(json.dumps(item) for item in content))

    report = check_file(file)

    assert report["is_check_passed"]
    assert report["utf8"]
    assert report["num_samples"] == len(content)
    assert report["has_min_samples"]


def test_check_jsonl_valid_instruction_multimodal(tmp_path: Path):
    file = tmp_path / "valid_instruction_multimodal.jsonl"
    content = [
        {
            "prompt": [
                {
                    "type": "text",
                    "text": "What's the difference between these two images?",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": "data:image/jpeg;base64,..."},
                },
                {
                    "type": "image_url",
                    "image_url": {"url": "data:image/jpeg;base64,..."},
                },
            ],
            "completion": "The first image is a cat, the second image is a dog.",
        },
    ]

    with file.open("w") as f:
        f.write("\n".join(json.dumps(item) for item in content))

    report = check_file(file)

    assert report["is_check_passed"]
    assert report["utf8"]
    assert report["num_samples"] == len(content)
    assert report["has_min_samples"]


def test_check_jsonl_valid_conversational_single_turn(tmp_path: Path):
    # Create a valid JSONL file with conversational format and 1 user-assistant turn pair
    file = tmp_path / "valid_conversational_single_turn.jsonl"
    content = [
        {
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ]
        },
        {
            "messages": [
                {"role": "user", "content": "How are you?"},
                {"role": "assistant", "content": "I am fine."},
            ]
        },
        {
            "messages": [
                {"role": "system", "content": "You are a kind AI"},
                {"role": "user", "content": "How are you?"},
                {"role": "assistant", "content": "I am fine."},
            ]
        },
    ]
    with file.open("w") as f:
        f.write("\n".join(json.dumps(item) for item in content))

    report = check_file(file)

    assert report["is_check_passed"]
    assert report["utf8"]
    assert report["num_samples"] == len(content)
    assert report["has_min_samples"]


def test_check_jsonl_valid_conversational_multiple_turns(tmp_path: Path):
    # Create a valid JSONL file with conversational format and multiple user-assistant turn pairs
    file = tmp_path / "valid_conversational_multiple_turns.jsonl"
    content = [
        {
            "messages": [
                {"role": "user", "content": "Is it going to rain today?"},
                {
                    "role": "assistant",
                    "content": "Yes, expect showers in the afternoon.",
                },
                {"role": "user", "content": "What is the weather like in Tokyo?"},
                {"role": "assistant", "content": "It is sunny with a chance of rain."},
            ]
        },
        {
            "messages": [
                {"role": "user", "content": "Who won the game last night?"},
                {"role": "assistant", "content": "The home team won by two points."},
                {"role": "user", "content": "What is the weather like in Amsterdam?"},
                {"role": "assistant", "content": "It is cloudy with a chance of snow."},
            ]
        },
        {
            "messages": [
                {"role": "system", "content": "You are a kind AI"},
                {"role": "user", "content": "Who won the game last night?"},
                {"role": "assistant", "content": "The home team won by two points."},
                {"role": "user", "content": "What is the weather like in Amsterdam?"},
                {"role": "assistant", "content": "It is cloudy with a chance of snow."},
            ]
        },
    ]
    with file.open("w") as f:
        f.write("\n".join(json.dumps(item) for item in content))

    report = check_file(file)

    assert report["is_check_passed"]
    assert report["utf8"]
    assert report["num_samples"] == len(content)
    assert report["has_min_samples"]


def test_check_jsonl_valid_conversational_multimodal_single_turn(tmp_path: Path):
    file = tmp_path / "valid_conversational_multimodal_single_turn.jsonl"
    content = [
        {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What's the difference between these two images?",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": "data:image/jpeg;base64,..."},
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": "data:image/jpeg;base64,..."},
                        },
                    ],
                },
                {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "Hi there!"}],
                },
            ]
        },
    ]

    with file.open("w") as f:
        f.write("\n".join(json.dumps(item) for item in content))

    report = check_file(file)

    assert report["is_check_passed"]
    assert report["utf8"]
    assert report["num_samples"] == len(content)
    assert report["has_min_samples"]


def test_check_jsonl_empty_file(tmp_path: Path):
    # Create an empty JSONL file
    file = tmp_path / "empty.jsonl"
    file.touch()

    report = check_file(file)

    assert not report["is_check_passed"]
    assert report["message"] == "File is empty"
    assert report["file_size"] == 0


def test_check_jsonl_non_utf8(tmp_path: Path):
    # Create a non-UTF-8 encoded JSONL file
    file = tmp_path / "non_utf8.jsonl"
    file.write_bytes(b"\xff\xfe\xfd")

    report = check_file(file)

    assert not report["is_check_passed"]
    assert not report["utf8"]
    assert "File is not UTF-8 encoded." in report["message"]


def test_check_jsonl_invalid_json(tmp_path: Path):
    # Create a JSONL file with invalid JSON
    file = tmp_path / "invalid_json.jsonl"
    content = [{"text": "Hello, world!"}, "Invalid JSON Line"]
    with file.open("w") as f:
        f.write("\n".join(json.dumps(item) for item in content))

    report = check_file(file)

    assert not report["is_check_passed"]
    assert "Error parsing file." in report["message"]


@pytest.mark.parametrize(
    "content",
    [
        pytest.param(
            [
                {"prompt": "Translate the following sentence.", "completion": "Hello, world!"},
                {"prompt": "Summarize the text."},
            ],
            id="missing_required_field",
        ),
        pytest.param(
            [
                {
                    "messages": [
                        {"role": "user", "content": "Hi"},
                        {"role": "assistant", "content": "Hi! How can I help you?"},
                    ]
                },
                {"text": "How are you?"},
            ],
            id="inconsistent_dataset_format",
        ),
        pytest.param(
            [{"messages": [{"role": "invalid_role", "content": "Hi"}]}],
            id="invalid_role",
        ),
        pytest.param(
            [{"messages": [{"role": "user", "content": "Hi"}]}],
            id="missing_assistant_role",
        ),
        pytest.param(
            [{"text": 123}],
            id="invalid_value_type",
        ),
        pytest.param(
            [{"messages": [{"role": "user", "content": "Hi"}, {"content": "Hello"}]}],
            id="missing_role_in_conversation",
        ),
        pytest.param(
            [{"messages": [{"role": "user"}]}],
            id="missing_content_in_conversation",
        ),
        pytest.param(
            [{"messages": [{"role": "assistant"}]}],
            id="missing_content_or_tool_calls_in_conversation",
        ),
        pytest.param(
            [
                {
                    "messages": [
                        "Hi!",
                        {"role": "user", "content": "Hi"},
                        {"role": "assistant"},
                    ]
                }
            ],
            id="wrong_turn_type",
        ),
        pytest.param(
            [{"text": "Hello, world!", "extra_column": "extra"}],
            id="extra_column",
        ),
        pytest.param(
            cast(List[Dict[str, Any]], [{"messages": []}]),
            id="empty_messages",
        ),
        pytest.param(
            [
                {
                    "messages": [
                        {"role": "user", "content": "Hello", "weight": 1.0},
                        {"role": "assistant", "content": "Hi there!", "weight": 0},
                    ]
                }
            ],
            id="invalid_weight_float",
        ),
        pytest.param(
            [
                {
                    "messages": [
                        {"role": "user", "content": "Hello", "weight": 2},
                        {"role": "assistant", "content": "Hi there!", "weight": 0},
                    ]
                }
            ],
            id="invalid_weight_value",
        ),
        pytest.param(
            [
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Hello"},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": "<malformed_base64_image>"},
                                },
                            ],
                        },
                        {
                            "role": "assistant",
                            "content": [{"type": "text", "text": "Hi there!"}],
                        },
                    ]
                }
            ],
            id="invalid_multimodal_content",
        ),
    ],
)
def test_check_jsonl_semantic_errors_pass_structural_check(tmp_path: Path, content: List[Dict[str, Any]]):
    # Semantic checks run on the server; client only verifies JSON objects per line.
    file = tmp_path / "semantic_error.jsonl"
    with file.open("w") as f:
        f.write("\n".join(json.dumps(item) for item in content))

    report = check_file(file)

    assert report["is_check_passed"]
    assert report["num_samples"] == len(content)


def test_check_jsonl_valid_weights_all_messages(tmp_path: Path):
    file = tmp_path / "valid_weights_all.jsonl"
    content = [
        {
            "messages": [
                {"role": "user", "content": "Hello", "weight": 1},
                {"role": "assistant", "content": "Hi there!", "weight": 0},
                {"role": "user", "content": "How are you?", "weight": 1},
                {"role": "assistant", "content": "I'm doing well!", "weight": 1},
            ]
        },
        {
            "messages": [
                {"role": "system", "content": "You are helpful", "weight": 0},
                {"role": "user", "content": "What's the weather?", "weight": 1},
                {"role": "assistant", "content": "It's sunny today!", "weight": 1},
            ]
        },
    ]
    with file.open("w") as f:
        f.write("\n".join(json.dumps(item) for item in content))

    report = check_file(file)
    assert report["is_check_passed"]
    assert report["num_samples"] == len(content)


def test_check_jsonl_valid_weights_mixed_with_none(tmp_path: Path):
    file = tmp_path / "valid_weights_mixed.jsonl"
    content = [
        {
            "messages": [
                {"role": "user", "content": "Hello", "weight": 1},
                {"role": "assistant", "content": "Hi there!", "weight": 0},
                {"role": "user", "content": "How are you?"},
                {"role": "assistant", "content": "I'm doing well!"},
            ]
        },
        {
            "messages": [
                {"role": "user", "content": "What's the weather?"},
                {"role": "assistant", "content": "It's sunny today!"},
            ]
        },
    ]
    with file.open("w") as f:
        f.write("\n".join(json.dumps(item) for item in content))

    report = check_file(file)
    assert report["is_check_passed"]
    assert report["num_samples"] == len(content)


def test_check_csv_valid_general(tmp_path: Path):
    # Create a valid CSV file
    file = tmp_path / "valid.csv"
    with open(file, "w") as f:
        writer = csv.DictWriter(f, fieldnames=["text"])
        writer.writeheader()
        writer.writerow({"text": "Hello, world!"})
        writer.writerow({"text": "How are you?"})

    report = check_file(file, purpose="eval")
    assert report["is_check_passed"]
    assert report["utf8"]
    assert report["num_samples"] == 2
    assert report["has_min_samples"]


def test_check_csv_empty_file(tmp_path: Path):
    # Create an empty CSV file
    file = tmp_path / "empty.csv"
    file.touch()

    report = check_file(file, purpose="eval")

    assert not report["is_check_passed"]
    assert report["message"] == "File is empty"
    assert report["file_size"] == 0


def test_check_csv_valid_completion(tmp_path: Path):
    # Create a valid CSV file with conversational format
    file = tmp_path / "valid_completion.csv"

    with open(file, "w") as f:
        writer = csv.DictWriter(f, fieldnames=["prompt", "completion"])
        writer.writeheader()
        writer.writerow(
            {
                "prompt": "Translate the following sentence.",
                "completion": "Hello, world!",
            }
        )

    report = check_file(file, purpose="eval")
    assert report["is_check_passed"]
    assert report["utf8"]
    assert report["num_samples"] == 1
    assert report["has_min_samples"]


def test_check_csv_invalid_column(tmp_path: Path):
    # Create a CSV file with an invalid column
    file = tmp_path / "invalid_column.csv"
    with open(file, "w") as f:
        writer = csv.DictWriter(f, fieldnames=["asfg"])
        writer.writeheader()

    report = check_file(file)

    assert not report["is_check_passed"]


def test_check_file_missing_path(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.jsonl"
    report = check_file(missing)
    assert not report["is_check_passed"]
    assert report["found"] is False
    assert "Checks passed" not in report["message"]
    assert "not found" in report["message"].lower() or "not a regular file" in report["message"].lower()


def test_check_file_unknown_extension(tmp_path: Path) -> None:
    f = tmp_path / "data.txt"
    f.write_text("notjson\n", encoding="utf-8")
    report = check_file(f)
    assert not report["is_check_passed"]
    assert "Unknown extension" in report["message"]
    assert report["message"] == report["filetype"]
