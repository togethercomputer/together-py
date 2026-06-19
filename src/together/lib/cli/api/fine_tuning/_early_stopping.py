from __future__ import annotations


def format_early_stopping_summary(
    early_stopped: bool | None,
    best_metric: float | None,
    best_step: int | None,
) -> str:
    if not early_stopped:
        return ""

    details = format_early_stopping_details(best_metric, best_step)
    if not details:
        return "early stopped"

    return f"early stopped: {details}"


def format_early_stopping_details(best_metric: float | None, best_step: int | None) -> str:
    details: list[str] = []

    if best_step is not None:
        step_label = "halt step" if best_metric is None else "best step"
        details.append(f"{step_label} {best_step}")

    if best_metric is not None:
        details.append(f"val loss {best_metric:.4g}")

    return ", ".join(details)
