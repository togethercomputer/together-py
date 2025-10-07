# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .evaluation_model_request_param import EvaluationModelRequestParam
from .evaluation_judge_model_config_param import EvaluationJudgeModelConfigParam

__all__ = [
    "EvaluationCreateParams",
    "Parameters",
    "ParametersEvaluationClassifyParameters",
    "ParametersEvaluationClassifyParametersModelToEvaluate",
    "ParametersEvaluationScoreParameters",
    "ParametersEvaluationScoreParametersModelToEvaluate",
    "ParametersEvaluationCompareParameters",
    "ParametersEvaluationCompareParametersModelA",
    "ParametersEvaluationCompareParametersModelB",
]


class EvaluationCreateParams(TypedDict, total=False):
    parameters: Required[Parameters]
    """Type-specific parameters for the evaluation"""

    type: Required[Literal["classify", "score", "compare"]]
    """The type of evaluation to perform"""


ParametersEvaluationClassifyParametersModelToEvaluate: TypeAlias = Union[str, EvaluationModelRequestParam]


class ParametersEvaluationClassifyParameters(TypedDict, total=False):
    input_data_file_path: Required[str]
    """Data file ID"""

    judge: Required[EvaluationJudgeModelConfigParam]

    labels: Required[SequenceNotStr[str]]
    """List of possible classification labels"""

    pass_labels: Required[SequenceNotStr[str]]
    """List of labels that are considered passing"""

    model_to_evaluate: ParametersEvaluationClassifyParametersModelToEvaluate
    """Field name in the input data"""


ParametersEvaluationScoreParametersModelToEvaluate: TypeAlias = Union[str, EvaluationModelRequestParam]


class ParametersEvaluationScoreParameters(TypedDict, total=False):
    input_data_file_path: Required[str]
    """Data file ID"""

    judge: Required[EvaluationJudgeModelConfigParam]

    max_score: Required[float]
    """Maximum possible score"""

    min_score: Required[float]
    """Minimum possible score"""

    pass_threshold: Required[float]
    """Score threshold for passing"""

    model_to_evaluate: ParametersEvaluationScoreParametersModelToEvaluate
    """Field name in the input data"""


ParametersEvaluationCompareParametersModelA: TypeAlias = Union[str, EvaluationModelRequestParam]

ParametersEvaluationCompareParametersModelB: TypeAlias = Union[str, EvaluationModelRequestParam]


class ParametersEvaluationCompareParameters(TypedDict, total=False):
    input_data_file_path: Required[str]
    """Data file name"""

    judge: Required[EvaluationJudgeModelConfigParam]

    model_a: ParametersEvaluationCompareParametersModelA
    """Field name in the input data"""

    model_b: ParametersEvaluationCompareParametersModelB
    """Field name in the input data"""


Parameters: TypeAlias = Union[
    ParametersEvaluationClassifyParameters, ParametersEvaluationScoreParameters, ParametersEvaluationCompareParameters
]
