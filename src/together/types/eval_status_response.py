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
    """Number of failed generations."""

    invalid_label_count: Optional[float] = None
    """Number of invalid labels"""

    judge_fail_count: Optional[float] = None
    """Number of failed judge generations"""

    label_counts: Optional[str] = None
    """JSON string representing label counts"""

    pass_percentage: Optional[float] = None
    """Pecentage of pass labels."""

    result_file_id: Optional[str] = None
    """Data File ID"""


class ResultsEvaluationScoreResultsAggregatedScores(BaseModel):
    mean_score: Optional[float] = None

    pass_percentage: Optional[float] = None

    std_score: Optional[float] = None


class ResultsEvaluationScoreResults(BaseModel):
    aggregated_scores: Optional[ResultsEvaluationScoreResultsAggregatedScores] = None

    failed_samples: Optional[float] = None
    """number of failed samples generated from model"""

    generation_fail_count: Optional[float] = None
    """Number of failed generations."""

    invalid_score_count: Optional[float] = None
    """number of invalid scores generated from model"""

    judge_fail_count: Optional[float] = None
    """Number of failed judge generations"""

    result_file_id: Optional[str] = None
    """Data File ID"""


class ResultsEvaluationCompareResults(BaseModel):
    a_wins: Optional[int] = FieldInfo(alias="A_wins", default=None)
    """Number of times model A won"""

    b_wins: Optional[int] = FieldInfo(alias="B_wins", default=None)
    """Number of times model B won"""

    generation_fail_count: Optional[float] = None
    """Number of failed generations."""

    judge_fail_count: Optional[float] = None
    """Number of failed judge generations"""

    num_samples: Optional[int] = None
    """Total number of samples compared"""

    result_file_id: Optional[str] = None
    """Data File ID"""

    ties: Optional[int] = FieldInfo(alias="Ties", default=None)
    """Number of ties"""


Results: TypeAlias = Union[
    ResultsEvaluationClassifyResults, ResultsEvaluationScoreResults, ResultsEvaluationCompareResults
]


class EvalStatusResponse(BaseModel):
    results: Optional[Results] = None
    """The results of the evaluation job"""

    status: Optional[Literal["completed", "error", "user_error", "running", "queued", "pending"]] = None
    """The status of the evaluation job"""
