from __future__ import annotations

import re

from cyclopts import App
from cyclopts.exceptions import CycloptsError

_UUID_RE = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$")

_COMMAND_ID_IDENTIFIERS = {
    "ft": re.compile(r"^ft-"),
    "fine-tuning": re.compile(r"^ft-"),
    "files": re.compile(r"^file-"),
    "evals": re.compile(r"^eval-"),
    "endpoints": re.compile(r"^endpoint-"),
    "beta clusters": _UUID_RE,
    "beta clusters storage": _UUID_RE,
    "beta clusters remediations": _UUID_RE,
    "beta jig volumes": _UUID_RE,
}


def _expand_implicit_retrieve_tokens(app: App, *tokens: str) -> list[str]:
    """
    Some commands (e.g. ft, eval, endpoint, cluster, volume) allow the user to provide an ID instead of a command.
    When this happens, we need to expand the tokens to include the retrieve command.
    For example, if the user runs "tg ft ft-12345678-90ab", we need to expand it to "tg ft retrieve ft-12345678-90ab".
    """

    (command_tokens, _app, args_tokens) = app.parse_commands(tokens)
    command = " ".join(list(command_tokens))

    regex = _COMMAND_ID_IDENTIFIERS.get(command)

    if len(args_tokens) == 0:
        return list(tokens)

    if regex and regex.match(args_tokens[0]):
        return list(command_tokens) + ["retrieve"] + list(args_tokens)

    return list(tokens)


def _long_option_names_in_tokens(tokens: list[str]) -> list[str]:
    names: list[str] = []
    for token in tokens:
        if token.startswith("--"):
            names.append(token.removeprefix("--").split("=", 1)[0])
    return names


def _legacy_command_before_first_option(tokens: list[str]) -> tuple[str, bool]:
    """Fallback when cyclopts cannot resolve a command chain (unknown invocations)."""
    parts: list[str] = []
    for token in tokens:
        if token.startswith("--"):
            break
        parts.append(token)
    is_beta_command = bool(parts and parts[0] == "beta")
    if is_beta_command:
        parts = parts[1:]
    return (" ".join(parts), is_beta_command)


# First subcommand token only (alias -> primary name) for stable telemetry.
_TELEMETRY_SUBCOMMAND_ALIASES: dict[str, str] = {"ft": "fine-tuning"}


def _canonical_telemetry_command(cmd: str) -> str:
    if not cmd:
        return cmd
    parts = cmd.split()
    primary = _TELEMETRY_SUBCOMMAND_ALIASES.get(parts[0])
    if primary is not None:
        parts[0] = primary
    parts = ["list" if p == "ls" else p for p in parts]
    parts = ["delete" if p == "-d" else p for p in parts]
    parts = ["create" if p == "-c" else p for p in parts]
    parts = ["retrieve" if p == "get" else p for p in parts]
    return " ".join(parts)


def preparse_tokens(app: App, tokens: list[str]) -> tuple[str, list[str], bool, list[str]]:
    """
    Return telemetry-safe command path (registered subcommands only), argument *names* from
    cyclopts resolution (including positional parameters — values are never returned), and
    whether the invocation is under ``beta``.

    Subcommand aliases (e.g. ``ft``) are normalized to their primary names (e.g. ``fine-tuning``).
    The ``list`` alias ``ls`` is normalized to ``list`` in the returned command path.
    The ``delete`` alias ``-d`` is normalized to ``delete`` in the returned command path.
    The ``create`` alias ``-c`` is normalized to ``create`` in the returned command path.
    The ``retrieve`` alias ``get`` is normalized to ``retrieve`` in the returned command path.
    Implicit ``retrieve`` for most commands is applied here so telemetry matches execution.

    Requires the root cyclopts :class:`~cyclopts.App` so positional values are not mistaken
    for subcommand tokens (e.g. ``beta jig secrets set <name> <value>``).

    Implicit ``retrieve`` for ``tg ft <job-id>`` is applied here so telemetry matches execution.
    """
    argv = list(tokens)
    argv = _expand_implicit_retrieve_tokens(app, *argv)
    chain, _, rest_after_chain = app.parse_commands(argv, include_parent_meta=False)
    legacy_cmd, legacy_beta = _legacy_command_before_first_option(argv)

    if chain:
        is_beta_command = chain[0] == "beta"
        chain_tail = list(chain[1:] if is_beta_command else chain)
        parsed_command = " ".join(chain_tail)
        # ``beta`` alone matches first; remaining tokens are not nested beta subcommands (invalid path).
        if chain == ("beta",) and rest_after_chain:
            parsed_command = legacy_cmd
    else:
        parsed_command = legacy_cmd
        is_beta_command = legacy_beta

    explicit_args: list[str] = []
    try:
        _, bound, _unused, _ignored = app.parse_known_args(argv)
        explicit_args.extend(bound.arguments.keys())
    except CycloptsError:
        explicit_args.extend(_long_option_names_in_tokens(rest_after_chain))

    return (_canonical_telemetry_command(parsed_command), explicit_args, is_beta_command, argv)
