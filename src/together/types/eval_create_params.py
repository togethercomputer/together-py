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
    model: Required[str]
    """Name of the judge model"""

    model_source: Required[Literal["serverless", "dedicated", "external"]]
    """Source of the judge model."""

    system_template: Required[str]
    """System prompt template for the judge"""

    external_api_token: str
    """Bearer/API token for external judge models."""

    external_base_url: str
    """Base URL for external judge models. Must be OpenAI-compatible base URL."""


class ParametersEvaluationClassifyParametersModelToEvaluateEvaluationModelRequest(TypedDict, total=False):
    input_template: Required[str]
    """Input prompt template"""

    max_tokens: Required[int]
    """Maximum number of tokens to generate"""

    model: Required[str]
    """Name of the model to evaluate"""

    model_source: Required[Literal["serverless", "dedicated", "external"]]
    """Source of the model."""

    system_template: Required[str]
    """System prompt template"""

    temperature: Required[float]
    """Sampling temperature"""

    external_api_token: str
    """Bearer/API token for external models."""

    external_base_url: str
    """Base URL for external models. Must be OpenAI-compatible base URL"""


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
    model: Required[str]
    """Name of the judge model"""

    model_source: Required[Literal["serverless", "dedicated", "external"]]
    """Source of the judge model."""

    system_template: Required[str]
    """System prompt template for the judge"""

    external_api_token: str
    """Bearer/API token for external judge models."""

    external_base_url: str
    """Base URL for external judge models. Must be OpenAI-compatible base URL."""


class ParametersEvaluationScoreParametersModelToEvaluateEvaluationModelRequest(TypedDict, total=False):
    input_template: Required[str]
    """Input prompt template"""

    max_tokens: Required[int]
    """Maximum number of tokens to generate"""

    model: Required[str]
    """Name of the model to evaluate"""

    model_source: Required[Literal["serverless", "dedicated", "external"]]
    """Source of the model."""

    system_template: Required[str]
    """System prompt template"""

    temperature: Required[float]
    """Sampling temperature"""

    external_api_token: str
    """Bearer/API token for external models."""

    external_base_url: str
    """Base URL for external models. Must be OpenAI-compatible base URL"""


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
    model: Required[str]
    """Name of the judge model"""

    model_source: Required[Literal["serverless", "dedicated", "external"]]
    """Source of the judge model."""

    system_template: Required[str]
    """System prompt template for the judge"""

    external_api_token: str
    """Bearer/API token for external judge models."""

    external_base_url: str
    """Base URL for external judge models. Must be OpenAI-compatible base URL."""


class ParametersEvaluationCompareParametersModelAEvaluationModelRequest(TypedDict, total=False):
    input_template: Required[str]
    """Input prompt template"""

    max_tokens: Required[int]
    """Maximum number of tokens to generate"""

    model: Required[str]
    """Name of the model to evaluate"""

    model_source: Required[Literal["serverless", "dedicated", "external"]]
    """Source of the model."""

    system_template: Required[str]
    """System prompt template"""

    temperature: Required[float]
    """Sampling temperature"""

    external_api_token: str
    """Bearer/API token for external models."""

    external_base_url: str
    """Base URL for external models. Must be OpenAI-compatible base URL"""


ParametersEvaluationCompareParametersModelA: TypeAlias = Union[
    str, ParametersEvaluationCompareParametersModelAEvaluationModelRequest
]


class ParametersEvaluationCompareParametersModelBEvaluationModelRequest(TypedDict, total=False):
    input_template: Required[str]
    """Input prompt template"""

    max_tokens: Required[int]
    """Maximum number of tokens to generate"""

    model: Required[str]
    """Name of the model to evaluate"""

    model_source: Required[Literal["serverless", "dedicated", "external"]]
    """Source of the model."""

    system_template: Required[str]
    """System prompt template"""

    temperature: Required[float]
    """Sampling temperature"""

    external_api_token: str
    """Bearer/API token for external models."""

    external_base_url: str
    """Base URL for external models. Must be OpenAI-compatible base URL"""


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
