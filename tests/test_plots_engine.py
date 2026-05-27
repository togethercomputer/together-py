from __future__ import annotations

import pytest

from together.lib.cli.components.plots._engine import (
    _interpolate,
    _uniform_grid,
    render_line_chart,
    render_sparklines,
)
from together.lib.cli.components.plot_finetune_metrics import _step_label


def constant_series(n: int = 5, value: float = 1.0) -> list[tuple[float, float]]:
    return [(float(i), value) for i in range(n)]


# Shared deterministic series used by golden-output tests
_LOSS = [(float(i), 1.0 - i * 0.1) for i in range(10)]  # 1.0 → 0.1
_ACCURACY = [(float(i), 0.5 + i * 0.05) for i in range(10)]  # 0.5 → 0.95
_WIDE = [(float(i), 10.0**i) for i in range(5)]  # 1, 10, 100, 1000, 10000

_LOSS_XS = [p[0] for p in _LOSS]
_LOSS_YS = [p[1] for p in _LOSS]
_ACCURACY_XS = [p[0] for p in _ACCURACY]
_ACCURACY_YS = [p[1] for p in _ACCURACY]
_WIDE_XS = [p[0] for p in _WIDE]
_WIDE_YS = [p[1] for p in _WIDE]


def _interp(xs: list[float], ys: list[float], x_grid: list[float]) -> list[float]:
    """Helper: interpolate a single series onto x_grid."""
    return _interpolate(xs, {"s": ys}, x_grid)["s"]


class TestInterpolate:
    def test_output_length_equals_grid(self) -> None:
        xs = [float(i) for i in range(10)]
        ys = [float(i) for i in range(10)]
        x_grid = _uniform_grid(xs, 5)
        result = _interp(xs, ys, x_grid)
        assert len(result) == 5

    def test_linear_data_interpolates_exactly(self) -> None:
        xs = [0.0, 9.0]
        ys = [0.0, 9.0]
        x_grid = _uniform_grid(xs, 10)
        result = _interp(xs, ys, x_grid)
        # grid points are 0.0, 0.9, 1.8, ..., 8.1 — y=x so values match
        assert result == pytest.approx(x_grid, abs=1e-9)  # type: ignore[misc]

    def test_constant_series_stays_constant(self) -> None:
        xs = [float(i) for i in range(20)]
        ys = [7.0] * 20
        x_grid = _uniform_grid(xs, 10)
        result = _interp(xs, ys, x_grid)
        assert result == pytest.approx([7.0] * 10, abs=1e-9)  # type: ignore[misc]

    def test_left_clamp(self) -> None:
        xs = [5.0, 9.0]
        ys = [99.0, 99.0]
        x_grid = _uniform_grid([0.0, 9.0], 10)
        result = _interp(xs, ys, x_grid)
        assert result == [99.0] * 10

    def test_right_clamp(self) -> None:
        xs = [0.0, 2.0]
        ys = [42.0, 42.0]
        x_grid = _uniform_grid([0.0, 9.0], 10)
        result = _interp(xs, ys, x_grid)
        assert result == [42.0] * 10

    def test_single_point_fills_all(self) -> None:
        xs = [5.0]
        ys = [3.14]
        x_grid = _uniform_grid([0.0, 9.0], 8)
        result = _interp(xs, ys, x_grid)
        assert result == [3.14] * 8

    def test_uniform_grid_length(self) -> None:
        assert len(_uniform_grid([0.0, 10.0], 5)) == 5

    def test_uniform_grid_endpoints(self) -> None:
        grid = _uniform_grid([0.0, 9.0], 10)
        assert grid[0] == pytest.approx(0.0)  # type: ignore[misc]
        assert grid[-1] == pytest.approx(9.0)  # type: ignore[misc]


class TestRenderSparklines:
    def test_empty_series_returns_no_data_message(self) -> None:
        result = render_sparklines("loss", [], [], width=20)
        assert result.plain == "No plottable data."

    def test_single_series_golden(self) -> None:
        result = render_sparklines("loss", _LOSS_XS, _LOSS_YS, width=20)
        assert result.plain == "      loss  ██▇▇▆▆▅▅▅▄▄▃▃▃▂▂▁▁    1 → 0.1\n"

    def test_constant_series_golden(self) -> None:
        _flat = constant_series(10, 5.0)
        result = render_sparklines("flat", [p[0] for p in _flat], [p[1] for p in _flat], width=20)
        assert result.plain == "      flat                        5 → 5\n"

    def test_single_point_golden(self) -> None:
        result = render_sparklines("single", [0.0], [1.0], width=20)
        assert result.plain == "    single                        1 → 1\n"

    def test_log_scale_golden(self) -> None:
        result = render_sparklines("wide", _WIDE_XS, _WIDE_YS, width=20, y_log=True)
        assert result.plain == "      wide   ▁▁▂▂▂▃▃▄▄▅▅▆▆▆▇▇███  1 → 1e+04\n"  # leading space = first sparkline block

    def test_label_width_truncates_with_ellipsis(self) -> None:
        result = render_sparklines("verylongname", _LOSS_XS, _LOSS_YS, width=20, label_width=6)
        # "verylongname" (12 chars) truncated to label_width=6: "ver..."
        assert result.plain.startswith("  ver...  ")

    def test_label_width_truncates_long_name_aligned(self) -> None:
        # A name longer than label_width is truncated with ..., staying aligned
        r1 = render_sparklines("loss", _LOSS_XS, _LOSS_YS, width=20, label_width=8)
        r2 = render_sparklines("averylongmetricname", _LOSS_XS, _LOSS_YS, width=20, label_width=8)
        assert r1.plain == "      loss  ██▇▇▆▆▅▅▅▄▄▃▃▃▂▂▁▁    1 → 0.1\n"  # right-justified
        assert r2.plain == "  avery...  ██▇▇▆▆▅▅▅▄▄▃▃▃▂▂▁▁    1 → 0.1\n"  # truncated to 8

    def test_aligned_across_calls(self) -> None:
        # Pass the same label_width to both calls → sparklines start at the same column
        shared_w = 8
        r1 = render_sparklines("loss", _LOSS_XS, _LOSS_YS, width=20, label_width=shared_w)
        r2 = render_sparklines("accuracy", _ACCURACY_XS, _ACCURACY_YS, width=20, label_width=shared_w)
        assert r1.plain == "      loss  ██▇▇▆▆▅▅▅▄▄▃▃▃▂▂▁▁    1 → 0.1\n"  # "loss" right-justified in 8
        assert r2.plain == "  accuracy    ▁▁▂▂▃▃▃▄▄▅▅▅▆▆▇▇██  0.5 → 0.95\n"  # "accuracy" fills 8 exactly

    @pytest.mark.parametrize(
        "bad_value, expected",
        [
            (float("-inf"), "      loss  ██▇▇▆▆▅▅▅▄  ▃▃▂▂▁▁    1 → 0.1\n"),
            (float("nan"), "      loss  ██▇▇▆▆▅▅▅▄  ▃▃▂▂▁▁    1 → 0.1\n"),
            (float("inf"), "      loss  ██▇▇▆▆▅▅▅▄██▃▃▂▂▁▁    1 → 0.1\n"),
        ],
        ids=["neg_inf", "nan", "pos_inf"],
    )
    def test_non_finite_rendered_as_extreme_block_golden(self, bad_value: float, expected: str) -> None:
        # -inf/NaN → blank (bottom) block; +inf → █ (top) block.
        xs = [float(i) for i in range(10)]
        ys = [(1.0 - i * 0.1) if i != 5 else bad_value for i in range(10)]
        result = render_sparklines("loss", xs, ys, width=20)
        assert result.plain == expected


class TestRenderLineChart:
    def test_empty_series_returns_no_data_message(self) -> None:
        result = render_line_chart([], {})
        assert result.plain == "No plottable data."

    def test_single_series_golden(self) -> None:
        result = render_line_chart(
            _LOSS_XS,
            {"loss": _LOSS_YS},
            width=20,
            height=4,
            n_xticks=3,
            x_label=_step_label,
        )
        assert result.plain == (
            "  loss  (0 – 9)  1 → 0.1\n"
            "       1┼───╮                \n"
            "     0.7┼   ╰─────╮          \n"
            "     0.4┼         ╰─────╮    \n"
            "     0.1┼               ╰─── \n"
            "        └┬─────────┬────────┬\n"
            "         0         4        9\n"
        )

    def test_multi_series_golden(self) -> None:
        # loss and accuracy share the same x-axis (steps 0–9)
        result = render_line_chart(
            _LOSS_XS,
            {"loss": _LOSS_YS, "accuracy": _ACCURACY_YS},
            width=20,
            height=4,
            n_xticks=3,
            x_label=_step_label,
        )
        assert result.plain == (
            "  loss  (0 – 9)  1 → 0.1\n"
            "  accuracy  (0 – 9)  0.5 → 0.95\n"
            "       1┼───╮          ╭──── \n"
            "     0.7┼  ╭───────────╯     \n"
            "     0.4┼──╯      ╰─────╮    \n"
            "     0.1┼               ╰─── \n"
            "        └┬─────────┬────────┬\n"
            "         0         4        9\n"
        )

    def test_log_scale_golden(self) -> None:
        result = render_line_chart(
            _WIDE_XS,
            {"metric": _WIDE_YS},
            width=20,
            height=4,
            n_xticks=3,
            x_label=_step_label,
            y_log=True,
        )
        assert result.plain == (
            "  metric  (0 – 4)  1 → 1e+04\n"
            "   1e+04┼              ╭──── \n"
            "     464┼         ╭────╯     \n"
            "    21.5┼ ╭───────╯          \n"
            "       1┼─╯                  \n"
            "        └┬─────────┬────────┬\n"
            "         0         2        4\n"
        )

    def test_constant_series_golden(self) -> None:
        _flat = constant_series(10, 42.0)
        result = render_line_chart(
            [p[0] for p in _flat],
            {"flat": [p[1] for p in _flat]},
            width=20,
            height=4,
            x_label=_step_label,
        )
        assert result.plain == (
            "  flat  (0 – 9)  42 → 42\n"
            "      42┼                    \n"
            "      42┼                    \n"
            "      42┼                    \n"
            "      42┼─────────────────── \n"
            "        └┬─────────┬────────┬\n"
            "         0         4        9\n"
        )

    def test_custom_x_label_golden(self) -> None:
        result = render_line_chart(
            _LOSS_XS,
            {"m": _LOSS_YS},
            width=20,
            height=4,
            n_xticks=3,
            x_label=lambda x: f"step{int(x)}",
        )
        assert result.plain == (
            "  m  (step0 – step9)  1 → 0.1\n"
            "       1┼───╮                \n"
            "     0.7┼   ╰─────╮          \n"
            "     0.4┼         ╰─────╮    \n"
            "     0.1┼               ╰─── \n"
            "        └┬─────────┬────────┬\n"
            "       step0     step4  step9\n"
        )

    @pytest.mark.parametrize(
        "bad_value, expected",
        [
            (
                float("-inf"),
                (
                    "  loss  (0 – 9)  1 → 0.1\n"
                    "       1┼───╮                \n"
                    "     0.7┼   ╰─────╮          \n"
                    "     0.4┼         │ ╭───╮    \n"
                    "     0.1┼         │ │   ╰─── \n"
                    "        └┬────────┴┬┴───────┬\n"
                    "         0         4        9\n"
                ),
            ),
            (
                float("nan"),
                (
                    "  loss  (0 – 9)  1 → 0.1\n"
                    "       1┼───╮                \n"
                    "     0.7┼   ╰──────          \n"
                    "     0.4┼           ────╮    \n"
                    "     0.1┼               ╰─── \n"
                    "        └┬─────────┬────────┬\n"
                    "         0         4        9\n"
                ),
            ),
            (
                float("inf"),
                (
                    "  loss  (0 – 9)  1 → 0.1\n"
                    "       1┼───╮     │ │        \n"
                    "     0.7┼   ╰─────╯ │        \n"
                    "     0.4┼           ╰───╮    \n"
                    "     0.1┼               ╰─── \n"
                    "        └┬─────────┬────────┬\n"
                    "         0         4        9\n"
                ),
            ),
        ],
        ids=["neg_inf", "nan", "pos_inf"],
    )
    def test_non_finite_rendered_as_extreme_golden(self, bad_value: float, expected: str) -> None:
        # -inf/NaN → dip to x-axis border; +inf → spike to top data row.
        xs = [float(i) for i in range(10)]
        ys = [(1.0 - i * 0.1) if i != 5 else bad_value for i in range(10)]
        result = render_line_chart(xs, {"loss": ys}, width=20, height=4, n_xticks=3, x_label=_step_label)
        assert result.plain == expected

    def test_label_width_caps_y_axis(self) -> None:
        # "1e+04" is exactly 5 chars; label_width=5 fits it without truncation
        result = render_line_chart(
            _WIDE_XS,
            {"metric": _WIDE_YS},
            width=20,
            height=4,
            x_label=_step_label,
            y_log=True,
            label_width=5,
        )
        assert result.plain == (
            "  metric  (0 – 4)  1 → 1e+04\n"
            "1e+04┼              ╭──── \n"
            "  464┼         ╭────╯     \n"
            " 21.5┼ ╭───────╯          \n"
            "    1┼─╯                  \n"
            "     └┬─────────┬────────┬\n"
            "      0         2        4\n"
        )
