from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils._exit import CliDiagnosticExit
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console

_UNSUPPORTED_MESSAGE = "Legacy endpoint restart is no longer supported."
_MIGRATION_GUIDANCE = (
    "Create a new endpoint, or migrate to v2 and restart a chosen deployment with explicit nonzero replica bounds: "
    "together beta endpoints update <deployment-id> --min-replicas <min> --max-replicas <max>"
)


async def start(
    endpoint_id: Annotated[
        str,
        Parameter(required=True, help="The ID of the endpoint to start"),
    ],
    wait: Annotated[bool, Parameter(help="Wait for the endpoint to start", negative=False)] = False,
    *,
    config: CLIConfigParameter,
) -> None:
    """Start a dedicated inference endpoint."""
    # Keep the command registered so existing users get actionable guidance instead
    # of an unknown-command error. The legacy API rejects restart, while v2 restart
    # requires a deployment choice and replica bounds that cannot be inferred safely.
    del endpoint_id, wait

    if config.json:
        console.print_json(
            openapi_dumps({"error": _UNSUPPORTED_MESSAGE, "migration_guidance": _MIGRATION_GUIDANCE}).decode("utf-8")
        )
    else:
        console.print(f"[red]Error:[/red] {_UNSUPPORTED_MESSAGE}")
        console.print(_MIGRATION_GUIDANCE)

    raise CliDiagnosticExit("Legacy endpoint restart is unsupported")
