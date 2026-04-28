from __future__ import annotations

import types
from typing import Union, Annotated, cast, get_args, get_origin
from pathlib import Path

from detect_agent import determine_agent
from cyclopts.help import HelpEntry, ColumnSpec, PlainFormatter, DefaultFormatter


def _is_union_origin(origin: object | None) -> bool:
    if origin is Union:
        return True
    ut = getattr(types, "UnionType", None)
    return ut is not None and origin is ut


# Define custom column renderers
def _names_renderer(entry: HelpEntry) -> str:
    """Combine parameter names and shorts."""
    is_command = entry.type is None

    # Commands
    if is_command:
        names = ", ".join(sorted(entry.names, key=len)).strip() if entry.names else ""
        short_part = ", ".join(entry.shorts).strip() if entry.shorts else ""
        if short_part:
            return f"{short_part}, {names}"
        return names

    # Parameters
    names = " ".join(entry.names[1:]) if entry.names else ""
    shorts = " ".join(entry.shorts) if entry.shorts else ""
    return " ".join([names, shorts]).strip()


def _strip_annotated_for_display(hint: object) -> object:
    """Unwrap Annotated[...], including inside Union / Optional / PEP 604 unions."""
    if hint is None:
        return hint
    origin = get_origin(hint)
    if origin is Annotated:
        return _strip_annotated_for_display(get_args(hint)[0])

    args = get_args(hint)
    if args and _is_union_origin(origin):
        parts = [_strip_annotated_for_display(a) for a in args]
        rebuilt: object = parts[0]
        for p in parts[1:]:
            rebuilt = rebuilt | p  # type: ignore[operator]
        return cast(object, rebuilt)

    return hint


type_short_name_to_display_name = {
    "Path": "Path",
    "str": "string",
    "int": "integer",
    "float": "float",
    "bool": "",
    "list": "list",
}


def _type_renderer(entry: HelpEntry) -> str:
    """Show the parameter type."""
    if entry.choices:
        return ", ".join(entry.choices)

    from cyclopts.annotations import resolve, get_hint_name  # type: ignore

    resolved_type = resolve(entry.type)

    # For our own special classes we can add a help_name to print a better type name
    # See BoolOrAuto in api/_utils.py
    internal_mod_help_name: str | None = getattr(resolved_type, "help_name", None)
    if internal_mod_help_name:
        return internal_mod_help_name

    if resolved_type is Path:
        return "path"

    hint = _strip_annotated_for_display(entry.type)
    typename = get_hint_name(hint) if hint else ""
    typename = typename.replace("|None", "").replace("|None", "")

    return type_short_name_to_display_name.get(typename, typename)


human_formatter = DefaultFormatter(
    column_specs=(
        ColumnSpec(
            renderer=lambda entry: "★" if entry.required else " ",
            width=1,
            style="yellow bold",
        ),
        ColumnSpec(
            renderer=_names_renderer,
            style="primary",
            max_width=30,
        ),
        ColumnSpec(
            renderer=_type_renderer,
            style="secondary",
        ),
        ColumnSpec(
            renderer="description",  # Use attribute name
            style="secondary",
            overflow="fold",
        ),
    )
)

agent_formatter = PlainFormatter()

help_formatter = agent_formatter if determine_agent()["is_agent"] else human_formatter
