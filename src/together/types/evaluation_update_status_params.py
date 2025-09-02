# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = [
    "EvaluationUpdateStatusParams",
    "Results",
    "ResultsEvaluationClassifyResults",
    "ResultsEvaluationScoreResults",
    "ResultsEvaluationScoreResultsAggregatedScores",
    "ResultsEvaluationCompareResults",
]


class EvaluationUpdateStatusParams(TypedDict, total=False):
    status: Required[Literal["completed", "error", "running", "queued", "user_error", "inference_error"]]
    """The new status for the job"""

    error: str
    """Error message"""

    results: Results


class ResultsEvaluationClassifyResults(TypedDict, total=False):
    generation_fail_count: Optional[float]
    """Number of failed generations."""

    invalid_label_count: Optional[float]
    """Number of invalid labels"""

    judge_fail_count: Optional[float]
    """Number of failed judge generations"""

    label_counts: str
    """JSON string representing label counts"""

    pass_percentage: Optional[float]
    """Pecentage of pass labels."""

    result_file_id: str
    """Data File ID"""


class ResultsEvaluationScoreResultsAggregatedScores(TypedDict, total=False):
    mean_score: float

    pass_percentage: float

    std_score: float


class ResultsEvaluationScoreResults(TypedDict, total=False):
    aggregated_scores: ResultsEvaluationScoreResultsAggregatedScores

    failed_samples: float
    """number of failed samples generated from model"""

    generation_fail_count: Optional[float]
    """Number of failed generations."""

    invalid_score_count: float
    """number of invalid scores generated from model"""

    judge_fail_count: Optional[float]
    """Number of failed judge generations"""

    result_file_id: str
    """Data File ID"""


class ResultsEvaluationCompareResults(TypedDict, total=False):
    a_wins: Annotated[int, PropertyInfo(alias="A_wins")]
    """Number of times model A won"""

    b_wins: Annotated[int, PropertyInfo(alias="B_wins")]
    """Number of times model B won"""

    generation_fail_count: Optional[float]
    """Number of failed generations."""

    judge_fail_count: Optional[float]
    """Number of failed judge generations"""

    num_samples: int
    """Total number of samples compared"""

    result_file_id: str
    """Data File ID"""

    ties: Annotated[int, PropertyInfo(alias="Ties")]
    """Number of ties"""


Results: TypeAlias = Union[
    ResultsEvaluationClassifyResults, ResultsEvaluationScoreResults, ResultsEvaluationCompareResults
]
