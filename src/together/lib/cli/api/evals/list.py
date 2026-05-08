from __future__ import annotations

from typing import Any, List, Literal, TypeVar, Optional, Annotated, cast

from cyclopts import Parameter

from together import omit
from together.types import EvaluationJob
from together.lib.utils import log_debug
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.types.evaluation_job import (
    ResultsEvaluationScoreResults,
    ResultsEvaluationCompareResults,
    ResultsEvaluationClassifyResults,
)
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.utils._mock_pagination import AfterParameter, mock_pagination

status_colors = {
    "pending": "yellow",
    "queued": "yellow",
    "running": "yellow",
    "error": "red",
    "user_error": "red",
    "completed": "green",
}


async def list(
    status: Annotated[
        Optional[Literal["pending", "queued", "running", "completed", "error", "user_error"]],
        Parameter(help="Filter evals by status"),
    ] = None,
    limit: Annotated[Optional[int], Parameter(help="The number of evals to return")] = None,
    after: AfterParameter = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List evals."""
    response = await show_loading_status(
        "Loading evals...", config.client.evals.list(status=status or omit, limit=limit or omit)
    )

    data, next_cursor = mock_pagination(response, cursor_field="workflow_id", cursor=after)

    if config.json:
        console.print_json(openapi_dumps(data).decode("utf-8"))
        return

    table = ListTable("Evals", empty_message="No evals found")
    table.add_primary_column("Workflow ID", ratio=1)
    table.add_column("Type", ratio=1)
    table.add_column("Result", ratio=4)

    for job in data:
        result = _get_result(job)
        table.add_row(
            f"[link=https://api.together.ai/evaluations/result/{job.workflow_id}]{job.workflow_id}[/link]",
            job.type,
            result,
        )
    console.print(table)
    if next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg evals list --after {next_cursor}[/white]")


T = TypeVar("T")


def _get_result(job: EvaluationJob) -> str:
    try:
        if job.status != "completed":
            status_color = status_colors[job.status] if job.status in status_colors else "white"
            return f"status: [{status_color}]{job.status}[/{status_color}]"

        if job.type == "score":
            score_job = cast(ResultsEvaluationScoreResults, job.results)
            return "\n".join(
                [
                    f"mean score: [primary]{getattr(score_job.aggregated_scores, 'mean_score', 'N/A')}[/primary]",
                    f"pass percentage: [primary]{getattr(score_job.aggregated_scores, 'pass_percentage', 'N/A')}[/primary]",
                    f"std score: [primary]{getattr(score_job.aggregated_scores, 'std_score', 'N/A')}[/primary]",
                ]
            )

        if job.type == "compare":
            compare_job = cast(ResultsEvaluationCompareResults, job.results)
            if (
                compare_job.a_wins is not None
                and compare_job.b_wins is not None
                and compare_job.a_wins > compare_job.b_wins
            ):
                return f"Winning Model: [primary]{_get_model_name(job, 'model_a')}[/primary] (model A)"
            elif (
                compare_job.b_wins is not None
                and compare_job.a_wins is not None
                and compare_job.b_wins > compare_job.a_wins
            ):
                return f"Winning Model: [primary]{_get_model_name(job, 'model_b')}[/primary] (model B)"
            else:
                return "[primary]Tie[/primary]"

        if job.type == "classify":
            classify_job = cast(ResultsEvaluationClassifyResults, job.results)
            if classify_job.label_counts is None:
                return "No label counts"

            labels = cast(
                dict[str, int], classify_job.label_counts
            )  # TODO: API has a bug in the shape of the response, so we need to cast it to the correct type
            return "\n".join(
                [
                    f"label: [primary]{label}[/primary] (count: [primary]{count}[/primary])"
                    for label, count in labels.items()
                ]
            )

        return ""
    except Exception as e:
        log_debug("Error parsing results for evals list", error=e)
        return "Internal error"


def deep_get(dictionary: dict[str, Any] | None, keys: List[str], default: T) -> T:
    cur = cast(Any, dictionary)
    for key in keys:
        if isinstance(cur, dict) and key in cur:
            cur = cast(Any, cur[key])
        else:
            return default
    return cast(T, cur)


def _get_model_name(job: EvaluationJob, field: str) -> str:
    """
    Get the name of the model to evaluate.

    Sometimes the parameters.model_to_evaluate is a dict, other times it's a string.
    """
    model: str | dict[str, Any] = deep_get(job.parameters, [field], "")

    if isinstance(model, dict):
        return deep_get(model, ["model"], "")

    return model
