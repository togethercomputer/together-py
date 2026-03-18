from __future__ import annotations

from typing import Annotated, Optional

from together._version import __version__
# from together._constants import DEFAULT_TIMEOUT
# from together.lib.cli.api.beta import beta
# from together.lib.cli.api.evals import evals
# from together.lib.cli.api.files import files
from detect_agent import determine_agent
from together.lib.cli.api.models.upload import upload
from together.lib.cli.api.models.list import list
# from together.lib.cli.api.endpoints import endpoints
# from together.lib.cli.api.fine_tuning import fine_tuning
from cyclopts import App, Parameter
from cyclopts.help import PlainFormatter, DefaultFormatter, ColumnSpec, HelpEntry

from together.lib.cli.api._utils import Config
from together.lib.cli.logger.console import console

# Define custom column renderers
def names_renderer(entry: HelpEntry) -> str:
    """Combine parameter names and shorts."""
    # Commands
    if len(entry.names) == 1:
        return entry.names[0]

    # Parameters
    names = " ".join(entry.names[1:]) if entry.names else ""
    shorts = " ".join(entry.shorts) if entry.shorts else ""
    return " ".join([names,shorts]).strip()

def type_renderer(entry: HelpEntry) -> str:
    """Show the parameter type."""
    if entry.choices:
        return ", ".join(entry.choices)
    
    from cyclopts.annotations import get_hint_name
    type = get_hint_name(entry.type) if entry.type else ""
    return type.replace("|None", "").replace("|None", "")

human_formatter = DefaultFormatter(
        column_specs=(
            ColumnSpec(
                renderer=lambda entry: "★" if entry.required else " ",
                header="",
                width=1,
                style="yellow bold",
            ),
            ColumnSpec(
                renderer=names_renderer,
                header="Option",
                style="cyan",
                max_width=30,
            ),
            ColumnSpec(
                renderer=type_renderer,
                header="Type",
                style="magenta",
                justify="center",
            ),
            ColumnSpec(
                renderer="description",  # Use attribute name
                header="Description",
                overflow="fold",
            ),
        )
    )

agent_formatter = PlainFormatter()

help_formatter = agent_formatter if determine_agent()["is_agent"] else human_formatter

app = App(
    name="tg",
    help_format="rich",
    help=f"[dim]Together CLI (v{__version__})[/dim]",
    version_flags=[],
    console=console,
    usage="",
    help_formatter=help_formatter,
)

@app.default()
async def default(_config: Annotated[Config | None, Parameter(name="*")] = None, version: Annotated[Optional[bool], Parameter("version", negative_bool="", help="Print application version.")] = None) -> None:
    if version:
        print(__version__)
        return
    app.help_print()

# Define Group objects here
models_app = App(name="models", help=f"Model management commands",
    help_format="rich",
    version_flags=[],
    usage="",
    help_on_error=True,
)
models_app.command(list, help_epilogue="""Examples:
  - List all models
    [primary]$ tg models list[/primary]

  - List all models that can be deployed on an endpoint:
    [primary]$ tg models list --type dedicated[/primary]

  - Continue pagination from a specific model ID:
    [primary]$ tg models list --after model.id[/primary]

  - Pipe the output in json format to jq for filtering (for example grabbing all the model ids):
    [primary]$ tg models list --json | jq '.[].id'[/primary]
""".strip())
models_app.command(upload, exit_on_error=False, help_on_error=True)

# models_app.command("together.lib.cli.api.models.list:app", name="list")
app.command(models_app)

def main() -> None:
    app()