from __future__ import annotations

from typing_extensions import override


class CliDiagnosticExit(SystemExit):
    """Exit with a diagnostic that command-failure telemetry can retain."""

    def __init__(self, message: str, code: int = 1) -> None:
        super().__init__(code)
        self.message = message

    @override
    def __str__(self) -> str:
        return self.message
