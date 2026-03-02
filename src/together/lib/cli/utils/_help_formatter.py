from pathlib import Path

from detect_agent import determine_agent
from cyclopts.help import HelpEntry, ColumnSpec, PlainFormatter, DefaultFormatter


# Define custom column renderers
def _names_renderer(entry: HelpEntry) -> str:
    """Combine parameter names and shorts."""
    # Commands
    if len(entry.names) == 1:
        return entry.names[0]

    # Parameters
    names = " ".join(entry.names[1:]) if entry.names else ""
    shorts = " ".join(entry.shorts) if entry.shorts else ""
    return " ".join([names, shorts]).strip()


def _type_renderer(entry: HelpEntry) -> str:
    """Show the parameter type."""
    if entry.choices:
        return ", ".join(entry.choices)

    from cyclopts.annotations import resolve, get_hint_name  # type: ignore

    resolved_type = resolve(entry.type)
    if resolved_type is Path:
        return "Path"

    type = get_hint_name(entry.type) if entry.type else ""
    return type.replace("|None", "").replace("|None", "")


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
