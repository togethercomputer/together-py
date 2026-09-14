"""ASCII sparkline and chart engine for time-series data.

Designed for scalar time-series (loss, accuracy, …); not a general-purpose
plotting library.

Internal pipeline (``_plot``, ``_interpolate``, …) uses a shared x-grid with
named y series: ``xs: list[float]`` + ``ys: dict[str, list[float]]``.

Public API
----------
``render_line_chart(xs, ys, ...)``
    One or more named series plotted on a shared ASCII line chart.  All series
    share the same x-axis and y-scale.

``render_sparklines(name, xs, ys, ...)``
    A single block-sparkline row (▁▂▃▄▅▆▇█).  Call once per series and pass a
    shared ``label_width`` across calls for consistent label alignment.  Names
    are right-justified; those that exceed ``label_width`` are truncated with
    ``...``.
"""

from __future__ import annotations

import math
import bisect
from typing import Callable

from rich.text import Text

_SPARK_BLOCKS = " ▁▂▃▄▅▆▇█"

# Styles cycled across series in insertion order.
_SERIES_STYLES = ["white", "green", "yellow", "cyan", "magenta"]

# UI style tokens used throughout the rendering pipeline.
_STYLE_PRIMARY = "primary"  # default plot body text
_STYLE_SECONDARY = "secondary"  # axis labels and tick text
_STYLE_ACCENT = "accent"  # axis border characters (┼ └ ┬ …)
_STYLE_MUTED = "muted"  # series name labels and empty-state messages
_STYLE_SPARK = "white"  # sparkline bar characters

# Sentinels used in quantized_ys to signal out-of-range non-finite values.
# Both are outside the valid slot range [0, height-1].
_NEG_INF_SENTINEL = -1  # -inf: line descends to the x-axis border
_POS_INF_SENTINEL = -2  # +inf: line ascends to the top data row
_NAN_SENTINEL = -3  #  NaN: no line at the place


def should_log(vals: list[float]) -> bool:
    """Return True when values span more than 100×, suggesting log scale."""
    positive_val = [v for v in vals if v > 0]
    return len(positive_val) > 1 and (max(positive_val) / min(positive_val)) > 100


def _uniform_grid(vals: list[float], n: int) -> list[float]:
    """Return n evenly-spaced points spanning [min(vals), max(vals)].

    Non-finite values (e.g. the -inf sentinel used for NaN data points) are
    excluded from the range computation so they don't corrupt the grid.
    """
    finite_val = [v for v in vals if math.isfinite(v)]
    min_val, max_val = min(finite_val), max(finite_val)
    if n <= 1:
        return [min_val]
    return [min_val + (max_val - min_val) * idx / (n - 1) for idx in range(n)]


def _interpolate(
    xs: list[float],
    ys: dict[str, list[float]],
    x_grid: list[float],
) -> dict[str, list[float]]:
    """Linearly interpolate each named y series onto x_grid; clamp at the edges.

    For each grid point:
    - If it falls before the first data point, use the first y value.
    - If it falls after the last data point, use the last y value.
    - Otherwise, linearly interpolate between the two bracketing data points.
    """
    results: dict[str, list[float]] = {}
    for name, yvals in ys.items():
        # Sort by x, using insertion order as a tiebreaker so that duplicate
        # steps are resolved deterministically (first occurrence wins).
        pairs = sorted(enumerate(zip(xs, yvals)), key=lambda t: (t[1][0], t[0]))
        xs_s = [x for _, (x, _y) in pairs]
        ys_s = [y for _, (_x, y) in pairs]

        interpolated: list[float] = []
        for x_point in x_grid:
            pos = bisect.bisect_left(xs_s, x_point)
            if pos == 0:
                interpolated.append(ys_s[0])
            elif pos == len(xs_s):
                interpolated.append(ys_s[-1])
            elif xs_s[pos] == x_point:
                interpolated.append(ys_s[pos])
            else:
                left_x, left_y = xs_s[pos - 1], ys_s[pos - 1]
                right_x, right_y = xs_s[pos], ys_s[pos]
                # When either bracket endpoint is a non-finite sentinel
                # (-inf/NaN or +inf) we cannot compute a meaningful slope.
                # Instead, assign this grid point to whichever bracket is
                # closer: if that bracket is non-finite the spike/dip extends
                # to this column; if it is finite we use its value so the
                # spike/dip stays as narrow as the grid resolution allows.
                if not math.isfinite(left_y) or not math.isfinite(right_y):
                    closer_y = left_y if (x_point - left_x) <= (right_x - x_point) else right_y
                    interpolated.append(closer_y)
                else:
                    slope = (right_y - left_y) / (right_x - left_x)
                    interpolated.append(left_y + slope * (x_point - left_x))

        results[name] = interpolated
    return results


def _log_transform(
    named_values: dict[str, list[float]],
) -> dict[str, list[float]]:
    """Return new traces with ys replaced by their log10 values."""
    result: dict[str, list[float]] = {}
    for name, values in named_values.items():
        nz = [value for value in values if value > 0]
        eps = min(nz) * 0.01 if nz else 1e-10
        result[name] = [math.log10(max(value, eps)) for value in values]
    return result


def _quantize_ys(
    interpolated_ys: dict[str, list[float]],
    y_grid: list[float],
) -> list[list[int]]:
    """Snap each interpolated y value to the index of the nearest y_grid slot.

    Non-finite values are mapped to out-of-band sentinels:

    * ``_NEG_INF_SENTINEL`` (``-1``) for ``-inf`` — the line descends to the
      x-axis border row.
    * ``_POS_INF_SENTINEL`` (``-2``) for ``+inf`` — the line spikes to the top
      data row.
    * ``_NAN_SENTINEL`` (``-3``) for ``NaN`` — no line is drawn at that point.
    """
    quantized_ys: list[list[int]] = []
    for ys in interpolated_ys.values():
        row: list[int] = []
        for y in ys:
            if math.isfinite(y):
                row.append(min(range(len(y_grid)), key=lambda i: abs(y_grid[i] - y)))
            elif y > 0:  # +inf
                row.append(_POS_INF_SENTINEL)
            elif math.isinf(y):
                row.append(_NEG_INF_SENTINEL)
            else:  # -inf or NaN (NaN > 0 is False)
                row.append(_NAN_SENTINEL)
        quantized_ys.append(row)
    return quantized_ys


def _fit_spark_label(name: str, label_width: int) -> str:
    """Right-justify *name* in *label_width* chars, truncating with '...' if needed."""
    if len(name) <= label_width:
        return name.rjust(label_width)
    return name[: max(0, label_width - 3)] + "..."


def _y_labels(
    y_grid: list[float],
    y_log: bool,
    y_label: Callable[[float], str],
) -> list[str]:
    """Build y-axis tick label strings from the y grid."""
    labels = [y_label(10**y) if y_log else y_label(y) for y in y_grid[::-1]]
    return labels


def _x_labels(
    x_grid: list[float],
    n_xticks: int,
    x_label: Callable[[float], str],
) -> list[tuple[int, str]]:
    """Return (column_index, label_string) pairs for each x-axis tick."""
    width = len(x_grid)
    x_min = x_grid[0]
    # Extend by one grid step beyond the last point so the rightmost tick
    # label shows the true data maximum.  round() suppresses floating-point
    # noise that would otherwise accumulate in the tick value calculations.
    x_max = round(x_grid[-1] + ((x_grid[-1] - x_grid[0]) / (width - 1) if width > 1 else 0.0), 10)
    if n_xticks < 2 or width <= 1:
        return [(0, x_label(x_min))]
    tick_cols = [round(i * (width - 1) / (n_xticks - 1)) for i in range(n_xticks)]
    tick_vals = [x_min + (x_max - x_min) * i / (n_xticks - 1) for i in range(n_xticks)]
    return [(col, x_label(val)) for col, val in zip(tick_cols, tick_vals)]


def _draw_y_axis(
    grid: list[list[str]],
    style_grid: list[list[str]],
    labels: list[str],
    label_w: int,
) -> None:
    """Fill y-axis labels and ┼ connectors into the grid."""
    for label, grid_row, style_row in zip(labels, grid, style_grid):
        if len(label) > label_w:
            label = label[: max(0, label_w - 3)] + "..."
        label = label.rjust(label_w)
        for ci, ch in enumerate(label):
            grid_row[ci] = ch
            style_row[ci] = _STYLE_SECONDARY
        grid_row[label_w] = "┼"
        style_row[label_w] = _STYLE_ACCENT


def _draw_lines(
    grid: list[list[str]],
    style_grid: list[list[str]],
    quantized_ys: list[list[int]],
    styles: list[str],
    label_w: int,
) -> frozenset[int]:
    """Draw all series into the shared grid (last writer wins on collision).

    Coordinate system: y_grid index 0 is the *bottom* of the data range, but
    grid row 0 is the *top* of the terminal output.  The conversion is:
        screen_row = len(grid) - y_grid_index - 1
    So a higher y_grid index means a higher data value and a *lower* screen row.

    Out-of-band sentinels (``_NEG_INF_SENTINEL``, ``_POS_INF_SENTINEL``) signal
    non-finite source values:

    * ``_NEG_INF_SENTINEL`` (-inf / NaN): line descends to the x-axis border.
      The set of affected plot-body column indices is returned so
      ``_draw_x_axis`` can mark them with ``┴``.
    * ``_POS_INF_SENTINEL`` (+inf): line spikes to the top data row (row 0).
    """
    height = len(grid)
    border_cols: set[int] = set()
    offset = label_w + 1
    width = len(grid[0])
    for style, pv in zip(styles, quantized_ys):
        # We look one column ahead (pv[col+1]), so stop one short of the end.
        for col_idx in range(width - label_w - 2):
            cur = pv[col_idx]
            nxt = pv[col_idx + 1]
            col = col_idx + offset

            cur_is_neg_inf = cur == _NEG_INF_SENTINEL
            nxt_is_neg_inf = nxt == _NEG_INF_SENTINEL
            cur_is_pos_inf = cur == _POS_INF_SENTINEL
            nxt_is_pos_inf = nxt == _POS_INF_SENTINEL
            cur_is_nan = cur == _NAN_SENTINEL
            nxt_is_nan = nxt == _NAN_SENTINEL

            # Two consecutive non-finite points of the same kind: nothing to draw.
            if (
                (cur_is_neg_inf and nxt_is_neg_inf)
                or (cur_is_pos_inf and nxt_is_pos_inf)
                or (cur_is_nan and nxt_is_nan)
            ):
                continue

            screen_row = height - cur - 1
            next_screen_row = height - nxt - 1

            # Recovering from border: │ up from bottom data row to nxt.
            if cur_is_neg_inf:
                border_cols.add(col_idx)
                grid[next_screen_row][col] = "╭"
                style_grid[next_screen_row][col] = style
                for mid_row in range(next_screen_row + 1, height):
                    grid[mid_row][col] = "│"
                    style_grid[mid_row][col] = style
                continue

            # Descending to border: │ down from cur to bottom data row.
            if nxt_is_neg_inf:
                border_cols.add(col_idx)
                grid[screen_row][col] = "╮"
                style_grid[screen_row][col] = style
                for mid_row in range(screen_row + 1, height):
                    grid[mid_row][col] = "│"
                    style_grid[mid_row][col] = style
                continue

            # Descending from top: │ down from row 0 to nxt.
            if cur_is_pos_inf:
                grid[0][col] = "│"
                style_grid[0][col] = style
                for mid_row in range(1, next_screen_row):
                    grid[mid_row][col] = "│"
                    style_grid[mid_row][col] = style
                grid[next_screen_row][col] = "╰"
                style_grid[next_screen_row][col] = style
                continue

            # Ascending to top: │ up from cur to row 0.
            if nxt_is_pos_inf:
                grid[screen_row][col] = "╯"
                style_grid[screen_row][col] = style
                for mid_row in range(1, screen_row):
                    grid[mid_row][col] = "│"
                    style_grid[mid_row][col] = style
                grid[0][col] = "│"
                style_grid[0][col] = style
                continue

            # Continue previous line if the next one is NaN
            if not cur_is_nan and nxt_is_nan:
                grid[screen_row][col] = "─"
                continue

            # Start a new line if the current one is nan, but the previous one is not
            if cur_is_nan and not nxt_is_nan:
                grid[next_screen_row][col] = "─"
                continue

            # If everything is finite and good, compare the values and add horizontal line or increasing/decreasing line
            if screen_row == next_screen_row:
                grid[screen_row][col] = "─"
                style_grid[screen_row][col] = style
                continue

            going_down = cur > nxt  # value decreases → line goes down on screen
            grid[screen_row][col] = "╮" if going_down else "╯"
            style_grid[screen_row][col] = style
            grid[next_screen_row][col] = "╰" if going_down else "╭"
            style_grid[next_screen_row][col] = style
            for mid_row in range(min(screen_row, next_screen_row) + 1, max(screen_row, next_screen_row)):
                grid[mid_row][col] = "│"
                style_grid[mid_row][col] = style

    return frozenset(border_cols)


def _draw_x_axis(
    grid: list[list[str]],
    style_grid: list[list[str]],
    label_w: int,
    x_labels: list[tuple[int, str]],
    nan_cols: frozenset[int] = frozenset(),
) -> None:
    """Append the └───┬─── border row and tick label row to the grid.

    ``nan_cols`` is a set of plot-body column indices (0-based within the plot
    body, i.e. not including the y-axis label area) where a NaN line descends
    to the border.  Those positions get ``┴`` instead of ``─``, or ``┼`` when
    they coincide with an x-tick ``┬``.
    """
    row_len = len(grid[0])
    width = row_len - label_w - 1

    # Border row: spaces | └ | ─ … ┬ … ─
    tick_cols = {col for col, _ in x_labels}
    border_chars = list("─" * width)
    for col in tick_cols:
        border_chars[col] = "┬"

    # Adding hitting lines to -inf to the border
    for col in nan_cols:
        if 0 <= col < width:
            border_chars[col] = "┼" if col in tick_cols else "┴"
    border_row = [" "] * label_w + ["└"] + border_chars
    border_styles = [_STYLE_SECONDARY] * label_w + [_STYLE_ACCENT] + [_STYLE_ACCENT] * width
    grid.append(border_row)
    style_grid.append(border_styles)

    # Label row: tick strings centred under their tick column
    label_row = [" "] * row_len
    for col, lbl in x_labels:
        start = label_w + 1 + col - len(lbl) // 2
        start = max(0, min(start, row_len - len(lbl)))
        for i, ch in enumerate(lbl):
            label_row[start + i] = ch
    grid.append(label_row)
    style_grid.append([_STYLE_SECONDARY] * row_len)


def _render_data_row(
    row: list[str],
    style_row: list[str],
) -> Text:
    """Colorize one grid row, appending each character with its style."""
    text = Text()
    for ch, style in zip(row, style_row):
        text.append(ch, style=style)
    text.append("\n")
    return text


def _render_body(
    grid: list[list[str]],
    style_grid: list[list[str]],
) -> Text:
    """Convert the finished grid into a Rich Text object."""
    text = Text()
    for row, style_row in zip(grid, style_grid):
        text.append_text(_render_data_row(row, style_row))
    return text


def _plot(
    xs: list[float],
    ys: dict[str, list[float]],
    *,
    width: int = 60,
    height: int = 6,
    x_label: Callable[[float], str] = str,
    y_label: Callable[[float], str] = str,
    y_log: bool = False,
    n_xticks: int = 3,
    label_width: int = 8,
) -> Text:
    """Render one or more named y series against a shared x-axis as an ASCII chart.

    Args:
        xs:           Shared x values for all series.
        ys:           Mapping of name → y values (must be same length as xs).
        width:        Number of character columns in the plot body.
        height:       Number of character rows in the chart body.
        x_label:      Callable that formats an x value into a tick-label string.
        y_label:      Callable that formats a y value into a tick-label string.
        y_log:        When True, values are plotted on a log10 axis.
        n_xticks:     Number of tick marks and labels on the x-axis (default 3).
        label_width:  Cap on the y-axis label column width (default 8).
                      Labels longer than this are truncated with ``...``.

    Returns:
        A ``rich.text.Text`` ready for ``console.print()``.
    """
    if not ys:
        t = Text()
        t.append("No data.", style=_STYLE_MUTED)
        return t

    ordered_styles = [_SERIES_STYLES[i % len(_SERIES_STYLES)] for i in range(len(ys))]

    x_grid = _uniform_grid(xs, width)
    interpolated_ys = _interpolate(xs, ys, x_grid)
    if y_log:
        interpolated_ys = _log_transform(interpolated_ys)
    flat_ys = [v for ys_list in interpolated_ys.values() for v in ys_list]
    y_grid = _uniform_grid(flat_ys, height)

    quantized_ys = _quantize_ys(interpolated_ys, y_grid)
    y_labels = _y_labels(y_grid, y_log, y_label)
    x_labels = _x_labels(x_grid, n_xticks, x_label)

    grid: list[list[str]] = [[" "] * (width + label_width + 1) for _ in range(height)]
    style_grid: list[list[str]] = [[_STYLE_PRIMARY] * (width + label_width + 1) for _ in range(height)]

    _draw_y_axis(grid, style_grid, y_labels, label_width)
    nan_cols = _draw_lines(grid, style_grid, quantized_ys, ordered_styles, label_width)
    _draw_x_axis(grid, style_grid, label_width, x_labels, nan_cols)

    text = _render_body(grid, style_grid)
    return text


def render_sparklines(
    name: str,
    xs: list[float],
    ys: list[float],
    *,
    width: int = 60,
    y_log: bool = False,
    label_width: int = 8,
) -> Text:
    """Render a single block-sparkline row for one series.

    Call once per series, passing a shared ``label_width`` across all calls to
    keep label columns aligned.  The name is right-justified within the column;
    names longer than ``label_width`` are truncated with ``...``.

    Args:
        name:        Series name, used as the row label.
        xs:          X values (e.g. training steps).
        ys:          Y values.
        width:       Sparkline character width (default 60).
        y_log:       When True, plot on a log10 scale (default False).
        label_width: Exact label column width (default 8).  Pass the same
                     value to every call in a group to get consistent
                     alignment.

    Returns:
        A ``rich.text.Text`` ready for ``console.print()``.
    """
    if not xs:
        t = Text()
        t.append("No plottable data.", style=_STYLE_MUTED)
        return t

    x_grid = _uniform_grid(xs, width)
    interpolated = _interpolate(xs, {name: ys}, x_grid)
    if y_log:
        interpolated = _log_transform(interpolated)

    series_vals = interpolated[name]
    y_grid = _uniform_grid(series_vals, len(_SPARK_BLOCKS))
    quantized = _quantize_ys({name: series_vals}, y_grid)[0]

    label = _fit_spark_label(name, label_width)

    # The sentinel value (len(y_grid)) indicates a NaN data point; render it
    # as a space (the lowest sparkline block) since sparklines have no border row.
    # Map out-of-band sentinels to the extreme sparkline blocks:
    # _NEG_INF_SENTINEL (-inf) or _NAN_SENTINEL (NaN) → space (lowest block, index 0)
    # _POS_INF_SENTINEL (+inf)        → █ (highest block, last index)
    def _spark_block(idx: int) -> str:
        if idx == _NEG_INF_SENTINEL or idx == _NAN_SENTINEL:
            return _SPARK_BLOCKS[0]
        if idx == _POS_INF_SENTINEL:
            return _SPARK_BLOCKS[-1]
        return _SPARK_BLOCKS[idx]

    spark = "".join(_spark_block(idx) for idx in quantized).ljust(width)

    text = Text()
    text.append(f"  {label}  ", style=_STYLE_MUTED)
    text.append(spark, style=_STYLE_SPARK)
    text.append(f"  {ys[0]:.4g} → {ys[-1]:.4g}", style=_STYLE_SECONDARY)
    text.append("\n")
    return text


def render_line_chart(
    xs: list[float],
    ys: dict[str, list[float]],
    *,
    x_label: Callable[[float], str] = str,
    y_log: bool = False,
    y_label: Callable[[float], str] | None = None,
    width: int = 60,
    height: int = 6,
    n_xticks: int = 3,
    label_width: int = 8,
) -> Text:
    """Render one or more named series as a shared ASCII line chart with a legend header.

    All series share the same x-axis (``xs``); each has its own named y values::

        console.print(
            render_line_chart(
                steps,
                {"train_loss": train_losses, "val_loss": val_losses},
                x_label=lambda s: f"step {s:.0f}",
            )
        )

    Args:
        xs:           Shared x values for all series.
        ys:           Mapping of name → y values.
        x_label:      Callable that formats an x value into a tick-label string.
        y_log:        When True, plot on a log10 y-axis (default False).
        y_label:      Callable that formats a y value into a tick-label string.
        width:        Plot width in terminal characters (default 60).
        height:       Plot height in terminal rows (default 6).
        n_xticks:     Number of x-axis tick marks and labels (default 3).
        label_width:  Cap on the y-axis label column width.

    Returns:
        A ``rich.text.Text`` ready for ``console.print()``.
    """
    if not ys:
        t = Text()
        t.append("No plottable data.", style=_STYLE_MUTED)
        return t

    styles = {key: _SERIES_STYLES[i % len(_SERIES_STYLES)] for i, key in enumerate(ys)}

    text = Text()
    x_from = x_label(xs[0])
    x_to = x_label(xs[-1])
    for key in ys:
        text.append(
            f"  {key}  ({x_from} – {x_to})  {ys[key][0]:.4g} → {ys[key][-1]:.4g}\n",
            style=styles[key],
        )

    text.append_text(
        _plot(
            xs,
            ys,
            width=width,
            height=height,
            x_label=x_label,
            y_label=y_label or (lambda v: f"{v:.3g}"),
            y_log=y_log,
            n_xticks=n_xticks,
            label_width=label_width,
        )
    )
    return text
