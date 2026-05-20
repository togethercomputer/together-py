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
    """Number of samples where model A was judged the winner"""

    b_wins: Optional[int] = FieldInfo(alias="B_wins", default=None)
    """Number of samples where model B was judged the winner"""

    generation_fail_count: Optional[float] = None
    """Number of generation failures across model A and model B."""

    judge_fail_count: Optional[float] = None
    """Number of judge inference failures.

    In the default two-pass mode (disable_position_bias_correction=false) this is
    the combined failure count from both the original-order and flipped-order judge
    passes.
    """

    result_file_id: Optional[str] = None
    """File ID of the detailed output file.

    Each row contains the original input fields plus judge outputs. In two-pass mode
    the file includes both original-order and flipped-order judge fields; in
    single-pass mode (disable_position_bias_correction=true) only original-order
    fields are present.
    """

    ties: Optional[int] = FieldInfo(alias="Ties", default=None)
    """Number of samples that resulted in a tie"""


Results: TypeAlias = Union[
    ResultsEvaluationClassifyResults, ResultsEvaluationScoreResults, ResultsEvaluationCompareResults
]


class EvalStatusResponse(BaseModel):
    results: Optional[Results] = None
    """The results of the evaluation job"""

    status: Optional[Literal["completed", "error", "user_error", "running", "queued", "pending"]] = None
    """The status of the evaluation job"""
