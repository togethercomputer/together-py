# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .._types import SequenceNotStr

__all__ = [
    "EvalCreateParams",
    "Parameters",
    "ParametersEvaluationClassifyParameters",
    "ParametersEvaluationClassifyParametersJudge",
    "ParametersEvaluationClassifyParametersModelToEvaluate",
    "ParametersEvaluationClassifyParametersModelToEvaluateEvaluationModelRequest",
    "ParametersEvaluationScoreParameters",
    "ParametersEvaluationScoreParametersJudge",
    "ParametersEvaluationScoreParametersModelToEvaluate",
    "ParametersEvaluationScoreParametersModelToEvaluateEvaluationModelRequest",
    "ParametersEvaluationCompareParameters",
    "ParametersEvaluationCompareParametersJudge",
    "ParametersEvaluationCompareParametersModelA",
    "ParametersEvaluationCompareParametersModelAEvaluationModelRequest",
    "ParametersEvaluationCompareParametersModelB",
    "ParametersEvaluationCompareParametersModelBEvaluationModelRequest",
]


class EvalCreateParams(TypedDict, total=False):
    parameters: Required[Parameters]
    """Type-specific parameters for the evaluation"""

    type: Required[Literal["classify", "score", "compare"]]
    """The type of evaluation to perform"""


class ParametersEvaluationClassifyParametersJudge(TypedDict, total=False):
    model_name: Required[str]
    """Name of the judge model"""

    system_template: Required[str]
    """System prompt template for the judge"""


class ParametersEvaluationClassifyParametersModelToEvaluateEvaluationModelRequest(TypedDict, total=False):
    input_template: Required[str]
    """Input prompt template"""

    max_tokens: Required[int]
    """Maximum number of tokens to generate"""

    model_name: Required[str]
    """Name of the model to evaluate"""

    system_template: Required[str]
    """System prompt template"""

    temperature: Required[float]
    """Sampling temperature"""


ParametersEvaluationClassifyParametersModelToEvaluate: TypeAlias = Union[
    str, ParametersEvaluationClassifyParametersModelToEvaluateEvaluationModelRequest
]


class ParametersEvaluationClassifyParameters(TypedDict, total=False):
    input_data_file_path: Required[str]
    """Data file ID"""

    judge: Required[ParametersEvaluationClassifyParametersJudge]

    labels: Required[SequenceNotStr[str]]
    """List of possible classification labels"""

    pass_labels: Required[SequenceNotStr[str]]
    """List of labels that are considered passing"""

    model_to_evaluate: ParametersEvaluationClassifyParametersModelToEvaluate
    """Field name in the input data"""


class ParametersEvaluationScoreParametersJudge(TypedDict, total=False):
    model_name: Required[str]
    """Name of the judge model"""

    system_template: Required[str]
    """System prompt template for the judge"""


class ParametersEvaluationScoreParametersModelToEvaluateEvaluationModelRequest(TypedDict, total=False):
    input_template: Required[str]
    """Input prompt template"""

    max_tokens: Required[int]
    """Maximum number of tokens to generate"""

    model_name: Required[str]
    """Name of the model to evaluate"""

    system_template: Required[str]
    """System prompt template"""

    temperature: Required[float]
    """Sampling temperature"""


ParametersEvaluationScoreParametersModelToEvaluate: TypeAlias = Union[
    str, ParametersEvaluationScoreParametersModelToEvaluateEvaluationModelRequest
]


class ParametersEvaluationScoreParameters(TypedDict, total=False):
    input_data_file_path: Required[str]
    """Data file ID"""

    judge: Required[ParametersEvaluationScoreParametersJudge]

    max_score: Required[float]
    """Maximum possible score"""

    min_score: Required[float]
    """Minimum possible score"""

    pass_threshold: Required[float]
    """Score threshold for passing"""

    model_to_evaluate: ParametersEvaluationScoreParametersModelToEvaluate
    """Field name in the input data"""


class ParametersEvaluationCompareParametersJudge(TypedDict, total=False):
    model_name: Required[str]
    """Name of the judge model"""

    system_template: Required[str]
    """System prompt template for the judge"""


class ParametersEvaluationCompareParametersModelAEvaluationModelRequest(TypedDict, total=False):
    input_template: Required[str]
    """Input prompt template"""

    max_tokens: Required[int]
    """Maximum number of tokens to generate"""

    model_name: Required[str]
    """Name of the model to evaluate"""

    system_template: Required[str]
    """System prompt template"""

    temperature: Required[float]
    """Sampling temperature"""


ParametersEvaluationCompareParametersModelA: TypeAlias = Union[
    str, ParametersEvaluationCompareParametersModelAEvaluationModelRequest
]


class ParametersEvaluationCompareParametersModelBEvaluationModelRequest(TypedDict, total=False):
    input_template: Required[str]
    """Input prompt template"""

    max_tokens: Required[int]
    """Maximum number of tokens to generate"""

    model_name: Required[str]
    """Name of the model to evaluate"""

    system_template: Required[str]
    """System prompt template"""

    temperature: Required[float]
    """Sampling temperature"""


ParametersEvaluationCompareParametersModelB: TypeAlias = Union[
    str, ParametersEvaluationCompareParametersModelBEvaluationModelRequest
]


class ParametersEvaluationCompareParameters(TypedDict, total=False):
    input_data_file_path: Required[str]
    """Data file name"""

    judge: Required[ParametersEvaluationCompareParametersJudge]

    model_a: ParametersEvaluationCompareParametersModelA
    """Field name in the input data"""

    model_b: ParametersEvaluationCompareParametersModelB
    """Field name in the input data"""


Parameters: TypeAlias = Union[
    ParametersEvaluationClassifyParameters, ParametersEvaluationScoreParameters, ParametersEvaluationCompareParameters
]
