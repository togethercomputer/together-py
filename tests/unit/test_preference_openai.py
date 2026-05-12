from __future__ import annotations

import json
from typing import Any
from pathlib import Path
from collections.abc import Callable

import pytest

from together.lib.utils.files import check_file

_TEST_PREFERENCE_OPENAI_CONTENT = [
    {
        "input": {
            "messages": [
                {"role": "user", "content": "Hi there, I have a question."},
                {"role": "assistant", "content": "Hello, how is your day going?"},
                {
                    "role": "user",
                    "content": "Hello, can you tell me how cold San Francisco is today?",
                },
            ],
        },
        "preferred_output": [
            {
                "role": "assistant",
                "content": "Today in San Francisco, it is not quite cold as expected. Morning clouds will give away "
                "to sunshine, with a high near 68°F (20°C) and a low around 57°F (14°C).",
            }
        ],
        "non_preferred_output": [
            {
                "role": "assistant",
                "content": "It is not particularly cold in San Francisco today.",
            }
        ],
    },
    {
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": "What's the best way to learn programming?",
                },
            ],
        },
        "preferred_output": [
            {
                "role": "assistant",
                "content": "The best way to learn programming is through consistent practice, working on real projects, "
                "and breaking down complex problems into smaller parts. Start with a beginner-friendly language like Python.",
            }
        ],
        "non_preferred_output": [{"role": "assistant", "content": "Just read some books and you'll be fine."}],
    },
]


def test_check_jsonl_valid_preference_openai(tmp_path: Path):
    """Test valid preference OpenAI format."""
    file = tmp_path / "valid_preference_openai.jsonl"
    content = _TEST_PREFERENCE_OPENAI_CONTENT
    with file.open("w") as f:
        f.write("\n".join(json.dumps(item) for item in content))

    report = check_file(file)

    assert report["is_check_passed"]
    assert report["utf8"]
    assert report["num_samples"] == len(content)
    assert report["has_min_samples"]


MISSING_FIELDS_TEST_CASES = [
    pytest.param("input", id="missing_input"),
    pytest.param("preferred_output", id="missing_preferred_output"),
    pytest.param("non_preferred_output", id="missing_non_preferred_output"),
]


@pytest.mark.parametrize("field_to_remove", MISSING_FIELDS_TEST_CASES)
def test_check_jsonl_invalid_preference_openai_missing_fields(tmp_path: Path, field_to_remove: str):
    """Test missing required fields in OpenAI preference format."""
    file = tmp_path / f"invalid_preference_openai_missing_{field_to_remove}.jsonl"
    content = [item.copy() for item in _TEST_PREFERENCE_OPENAI_CONTENT]

    # Remove the specified field from the first item
    del content[0][field_to_remove]

    with file.open("w") as f:
        f.write("\n".join(json.dumps(item) for item in content))

    report = check_file(file)

    assert report["is_check_passed"], "Client-side check is structural only; server validates preference schema"


STRUCTURAL_ISSUE_TEST_CASES = [
    pytest.param(
        "empty_messages",
        lambda item: item.update({"input": {"messages": []}}),  # type: ignore[arg-type]
        id="empty_messages",
    ),
    pytest.param(
        "missing_role_preferred",
        lambda item: item.update(  # type: ignore[arg-type]
            {"preferred_output": [{"content": "Missing role field"}]}
        ),
        id="missing_role_preferred",
    ),
    pytest.param(
        "missing_role_non_preferred",
        lambda item: item.update(  # type: ignore[arg-type]
            {"non_preferred_output": [{"content": "Missing role field"}]}
        ),
        id="missing_role_non_preferred",
    ),
    pytest.param(
        "missing_content_preferred",
        lambda item: item.update({"preferred_output": [{"role": "assistant"}]}),  # type: ignore[arg-type]
        id="missing_content_preferred",
    ),
    pytest.param(
        "missing_content_non_preferred",
        lambda item: item.update({"non_preferred_output": [{"role": "assistant"}]}),  # type: ignore[arg-type]
        id="missing_content_non_preferred",
    ),
    pytest.param(
        "wrong_output_format_preferred",
        lambda item: item.update({"preferred_output": "Not an array but a string"}),  # type: ignore[arg-type]
        id="wrong_output_format_preferred",
    ),
    pytest.param(
        "wrong_output_format_non_preferred",
        lambda item: item.update({"non_preferred_output": "Not an array but a string"}),  # type: ignore[arg-type]
        id="wrong_output_format_non_preferred",
    ),
    pytest.param(
        "missing_content",
        lambda item: item.update({"input": {"messages": [{"role": "user"}]}}),  # type: ignore[arg-type]
        id="missing_content",
    ),
    pytest.param(
        "multiple_preferred_outputs",
        lambda item: item.update(  # type: ignore[arg-type]
            {
                "preferred_output": [
                    {"role": "assistant", "content": "First response"},
                    {"role": "assistant", "content": "Second response"},
                ]
            }
        ),
        id="multiple_preferred_outputs",
    ),
    pytest.param(
        "multiple_non_preferred_outputs",
        lambda item: item.update(  # type: ignore[arg-type]
            {
                "non_preferred_output": [
                    {"role": "assistant", "content": "First response"},
                    {"role": "assistant", "content": "Second response"},
                ]
            }
        ),
        id="multiple_non_preferred_outputs",
    ),
    pytest.param(
        "empty_preferred_output",
        lambda item: item.update({"preferred_output": []}),  # type: ignore[arg-type]
        id="empty_preferred_output",
    ),
    pytest.param(
        "empty_non_preferred_output",
        lambda item: item.update({"non_preferred_output": []}),  # type: ignore[arg-type]
        id="empty_non_preferred_output",
    ),
    pytest.param(
        "non_string_content_in_messages",
        lambda item: item.update(  # type: ignore[arg-type]
            {"input": {"messages": [{"role": "user", "content": 123}]}}
        ),
        id="non_string_content_in_messages",
    ),
    pytest.param(
        "invalid_role_in_messages",
        lambda item: item.update(  # type: ignore[arg-type]
            {"input": {"messages": [{"role": "invalid_role", "content": "Hello"}]}}
        ),
        id="invalid_role_in_messages",
    ),
    pytest.param(
        "invalid_weight_type",
        lambda item: item.update(  # type: ignore[arg-type]
            {"input": {"messages": [{"role": "user", "content": "Hello", "weight": "not_an_integer"}]}}
        ),
        id="invalid_weight_type",
    ),
    pytest.param(
        "invalid_weight_value",
        lambda item: item.update(  # type: ignore[arg-type]
            {"input": {"messages": [{"role": "user", "content": "Hello", "weight": 2}]}}
        ),
        id="invalid_weight_value",
    ),
    pytest.param(
        "non_dict_message",
        lambda item: item.update({"input": {"messages": ["Not a dictionary"]}}),  # type: ignore[arg-type]
        id="non_dict_message",
    ),
    pytest.param(
        "non_dict_input",
        lambda item: item.update({"input": "Not a dictionary"}),  # type: ignore[arg-type]
        id="non_dict_input",
    ),
    pytest.param(
        "missing_messages_in_input",
        lambda item: item.update({"input": {}}),  # type: ignore[arg-type]
        id="missing_messages_in_input",
    ),
    pytest.param(
        "non_assistant_role_in_preferred",
        lambda item: item.update(  # type: ignore[arg-type]
            {"preferred_output": [{"role": "user", "content": "This should be assistant"}]}
        ),
        id="non_assistant_role_in_preferred",
    ),
    pytest.param(
        "non_assistant_role_in_non_preferred",
        lambda item: item.update(  # type: ignore[arg-type]
            {"non_preferred_output": [{"role": "user", "content": "This should be assistant"}]}
        ),
        id="non_assistant_role_in_non_preferred",
    ),
]


@pytest.mark.parametrize(("name", "modifier"), STRUCTURAL_ISSUE_TEST_CASES)
def test_check_jsonl_invalid_preference_openai_structural_issues(
    tmp_path: Path,
    name: str,
    modifier: Callable[[dict[str, Any]], None],
):
    """Test various structural issues in OpenAI preference format."""
    file = tmp_path / f"invalid_preference_openai_{name}.jsonl"
    content = [item.copy() for item in _TEST_PREFERENCE_OPENAI_CONTENT]

    # Apply the modification to the first item
    modifier(content[0])

    with file.open("w") as f:
        f.write("\n".join(json.dumps(item) for item in content))

    report = check_file(file)

    assert report["is_check_passed"], "Client-side check is structural only; server validates preference schema"
