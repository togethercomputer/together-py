# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "EvaluationJob",
    "Results",
    "ResultsEvaluationClassifyResults",
    "ResultsEvaluationScoreResults",
    "ResultsEvaluationScoreResultsAggregatedScores",
    "ResultsEvaluationCompareResults",
    "ResultsError",
    "StatusUpdate",
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


class ResultsError(BaseModel):
    error: Optional[str] = None


Results: TypeAlias = Union[
    ResultsEvaluationClassifyResults, ResultsEvaluationScoreResults, ResultsEvaluationCompareResults, ResultsError, None
]


class StatusUpdate(BaseModel):
    message: Optional[str] = None
    """Additional message for this update"""

    status: Optional[str] = None
    """The status at this update"""

    timestamp: Optional[datetime] = None
    """When this update occurred"""


class EvaluationJob(BaseModel):
    created_at: Optional[datetime] = None
    """When the job was created"""

    owner_id: Optional[str] = None
    """ID of the job owner (admin only)"""

    parameters: Optional[Dict[str, object]] = None
    """The parameters used for this evaluation"""

    results: Optional[Results] = None
    """Results of the evaluation (when completed)"""

    status: Optional[Literal["pending", "queued", "running", "completed", "error", "user_error"]] = None
    """Current status of the job"""

    status_updates: Optional[List[StatusUpdate]] = None
    """History of status updates (admin only)"""

    type: Optional[Literal["classify", "score", "compare"]] = None
    """The type of evaluation"""

    updated_at: Optional[datetime] = None
    """When the job was last updated"""

    workflow_id: Optional[str] = None
    """The evaluation job ID"""
