from __future__ import annotations

import pytest

from together.lib.cli import app


@pytest.mark.parametrize(
    "remote",
    [
        ["echo", "hello", "world"],
        ["bash", "-lc", "printf '%s' hello"],
        ["python", "-u", "script.py", "--verbose"],
        ["printf", "%s", "--json", "--project", "remote-project"],
    ],
)
def test_strict_parser_preserves_declared_ssh_passthrough(remote: list[str]) -> None:
    # Parse the real registered command without authenticating or executing SSH.
    tokens = ["clusters", "ssh", "https://dex.example/cluster", "--login", "alice", "--", *remote]
    known_command, known_bound, unused, known_extra = app.parse_known_args(tokens)
    command, bound, extra = app.parse_args(tokens)
    assert unused == []
    assert command is known_command
    assert bound.arguments == known_bound.arguments
    assert bound.arguments["remote_command"] == tuple(remote)
    assert extra == known_extra


def test_strict_parser_preserves_stdout_filename() -> None:
    _, bound, _ = app.parse_args(["clusters", "get-credentials", "cluster-1", "--file", "-"])
    assert bound.arguments["file"] == "-"


def test_strict_parser_accepts_hyphenated_positional_after_delimiter() -> None:
    _, bound, _ = app.parse_args(["models", "configs", "--", "-model-name"])
    assert bound.arguments["model"] == "-model-name"
