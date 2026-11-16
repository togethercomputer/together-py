# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "EvalStatusResponse",
    "Results",
    "ResultsEvaluationClassifyResults",
    "ResultsEvaluationScoreResults",
    "ResultsEvaluationScoreResultsAggregatedScores",
    "ResultsEvaluationCompareResults",
]


class ResultsEvaluationClassifyResults(BaseModel):
    generation_fail_count: Optional[float] = None

    invalid_label_count: Optional[float] = None

    judge_fail_count: Optional[float] = None

    label_counts: Optional[str] = None

    pass_percentage: Optional[float] = None

    result_file_id: Optional[str] = None


class ResultsEvaluationScoreResultsAggregatedScores(BaseModel):
    mean_score: Optional[float] = None

    pass_percentage: Optional[float] = None

    std_score: Optional[float] = None


class ResultsEvaluationScoreResults(BaseModel):
    aggregated_scores: Optional[ResultsEvaluationScoreResultsAggregatedScores] = None

    failed_samples: Optional[float] = None

    generation_fail_count: Optional[float] = None

    invalid_score_count: Optional[float] = None

    judge_fail_count: Optional[float] = None

    result_file_id: Optional[str] = None


class ResultsEvaluationCompareResults(BaseModel):
    a_wins: Optional[int] = FieldInfo(alias="A_wins", default=None)

    b_wins: Optional[int] = FieldInfo(alias="B_wins", default=None)

    generation_fail_count: Optional[float] = None

    judge_fail_count: Optional[float] = None

    result_file_id: Optional[str] = None

    ties: Optional[int] = FieldInfo(alias="Ties", default=None)


Results: TypeAlias = Union[
    ResultsEvaluationClassifyResults, ResultsEvaluationScoreResults, ResultsEvaluationCompareResults
]


class EvalStatusResponse(BaseModel):
    results: Optional[Results] = None

    status: Optional[Literal["completed", "error", "user_error", "running", "queued", "pending"]] = None
