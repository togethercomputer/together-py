"""Generic CLI plot utilities."""

from together.lib.cli.components.plots._engine import should_log, render_line_chart, render_sparklines

__all__ = [
    "render_line_chart",
    "render_sparklines",
    "should_log",
]
