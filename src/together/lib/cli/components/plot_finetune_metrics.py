"""Fine-tuning metrics plotting utilities.

Public API
----------
``metrics_block_sparklines(metrics)``
    One ▁▂▃▄▅▆▇█ sparkline line per metric — used in ``retrieve``.

``metrics_ascii_charts(metrics, height=6)``
    One full ASCII line chart per metric — used in ``list-metrics``.
"""

from __future__ import annotations

import math
from typing import Any
from collections import defaultdict

from rich.text import Text

from together.lib.cli.components.plots import should_log, render_line_chart, render_sparklines

# Columns reserved for the y-axis label area, ┼ connector, leading indent, and
# surrounding margin in the ASCII chart layout.  This must be >= label_width + 1
# (the default label_width used in metrics_ascii_charts is 8, so the minimum is
# 9).  Callers subtract this from the terminal width to get the usable plot width.
METRICS_WIDTH_PADDING = 48

_SKIP_KEYS: frozenset[str] = frozenset({"timestamp", "step", "global_step", "epoch"})


def _is_skip(k: str) -> bool:
    base = k.rsplit("/", 1)[-1]
    return base in _SKIP_KEYS or base.endswith("_step") or base.endswith("_epoch")


def _step_label(x: float) -> str:
    return str(int(x))


def _collect_series(
    metrics: list[dict[str, Any]],
) -> dict[str, tuple[list[float], list[float]]]:
    """Collect plottable numeric series from a list of metric dicts.

    Returns a mapping of name → (xs, ys).  Keys are discovered in insertion
    order; step/epoch/timestamp fields are skipped.  NaN values are converted
    to ``-inf`` so the rendering engine plots them at the very bottom of the
    chart rather than silently dropping them.
    """
    series: dict[str, tuple[list[float], list[float]]] = defaultdict(lambda: ([], []))
    for row in metrics:
        step = float(row["train/global_step"])
        for k, v in row.items():
            if _is_skip(k) or isinstance(v, bool) or not isinstance(v, (int, float)):
                continue
            val = float(v)
            # NaN is rendered as a dip to the bottom (-inf sentinel).
            if math.isnan(val):
                val = float("-inf")
            series[k][0].append(step)
            series[k][1].append(val)
    return series


def _no_data() -> Text:
    t = Text()
    t.append("No plottable metrics found.", style="muted")
    return t


def metrics_block_sparklines(
    metrics: list[dict[str, Any]],
    *,
    width: int = 60,
) -> Text:
    """One block-sparkline line per metric, coloured with the CLI theme.

    Args:
        metrics: List of flat metric dicts (one per training step).
        width:   Sparkline character width (default 60).

    Returns:
        A ``rich.text.Text`` ready for ``console.print()``.
    """
    series = _collect_series(metrics)
    if not series:
        return _no_data()
    label_w = max(len(k) for k in series)
    text = Text()
    for key, (xs, ys) in series.items():
        text.append_text(
            render_sparklines(
                key,
                xs,
                ys,
                width=width,
                y_log=should_log(ys),
                label_width=label_w,
            )
        )
    return text


def metrics_ascii_charts(
    metrics: list[dict[str, Any]],
    *,
    height: int = 6,
    width: int = 60,
    label_width: int = 8,
) -> Text:
    """One ASCII line chart per metric, with a global-step x-axis.

    Args:
        metrics: List of flat metric dicts (one per training step).
        height:  Chart body height in rows (default 6).
        width:   Plot character width (default 60).

    Returns:
        A ``rich.text.Text`` ready for ``console.print()``.
    """
    series = _collect_series(metrics)
    text = Text()
    for key, (xs, ys) in series.items():
        if text:
            text.append("\n")
        text.append_text(
            render_line_chart(
                xs,
                {key: ys},
                x_label=_step_label,
                y_log=should_log(ys),
                height=height,
                width=width,
                label_width=label_width,
            )
        )
    return text if text else _no_data()


__all__ = [
    "metrics_block_sparklines",
    "metrics_ascii_charts",
    "METRICS_WIDTH_PADDING",
]
