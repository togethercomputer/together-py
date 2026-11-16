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

    type: Required[Literal["classify", "score", "compare"]]


class ParametersEvaluationClassifyParametersJudge(TypedDict, total=False):
    model: Required[str]

    model_source: Required[Literal["serverless", "dedicated", "external"]]

    system_template: Required[str]

    external_api_token: str

    external_base_url: str

    max_tokens: int

    num_workers: int

    temperature: float


class ParametersEvaluationClassifyParametersModelToEvaluateEvaluationModelRequest(TypedDict, total=False):
    input_template: Required[str]

    max_tokens: Required[int]

    model: Required[str]

    model_source: Required[Literal["serverless", "dedicated", "external"]]

    system_template: Required[str]

    temperature: Required[float]

    external_api_token: str

    external_base_url: str

    num_workers: int


ParametersEvaluationClassifyParametersModelToEvaluate: TypeAlias = Union[
    str, ParametersEvaluationClassifyParametersModelToEvaluateEvaluationModelRequest
]


class ParametersEvaluationClassifyParameters(TypedDict, total=False):
    input_data_file_path: Required[str]

    judge: Required[ParametersEvaluationClassifyParametersJudge]

    labels: Required[SequenceNotStr[str]]

    pass_labels: Required[SequenceNotStr[str]]

    model_to_evaluate: ParametersEvaluationClassifyParametersModelToEvaluate


class ParametersEvaluationScoreParametersJudge(TypedDict, total=False):
    model: Required[str]

    model_source: Required[Literal["serverless", "dedicated", "external"]]

    system_template: Required[str]

    external_api_token: str

    external_base_url: str

    max_tokens: int

    num_workers: int

    temperature: float


class ParametersEvaluationScoreParametersModelToEvaluateEvaluationModelRequest(TypedDict, total=False):
    input_template: Required[str]

    max_tokens: Required[int]

    model: Required[str]

    model_source: Required[Literal["serverless", "dedicated", "external"]]

    system_template: Required[str]

    temperature: Required[float]

    external_api_token: str

    external_base_url: str

    num_workers: int


ParametersEvaluationScoreParametersModelToEvaluate: TypeAlias = Union[
    str, ParametersEvaluationScoreParametersModelToEvaluateEvaluationModelRequest
]


class ParametersEvaluationScoreParameters(TypedDict, total=False):
    input_data_file_path: Required[str]

    judge: Required[ParametersEvaluationScoreParametersJudge]

    max_score: Required[float]

    min_score: Required[float]

    pass_threshold: Required[float]

    model_to_evaluate: ParametersEvaluationScoreParametersModelToEvaluate


class ParametersEvaluationCompareParametersJudge(TypedDict, total=False):
    model: Required[str]

    model_source: Required[Literal["serverless", "dedicated", "external"]]

    system_template: Required[str]

    external_api_token: str

    external_base_url: str

    max_tokens: int

    num_workers: int

    temperature: float


class ParametersEvaluationCompareParametersModelAEvaluationModelRequest(TypedDict, total=False):
    input_template: Required[str]

    max_tokens: Required[int]

    model: Required[str]

    model_source: Required[Literal["serverless", "dedicated", "external"]]

    system_template: Required[str]

    temperature: Required[float]

    external_api_token: str

    external_base_url: str

    num_workers: int


ParametersEvaluationCompareParametersModelA: TypeAlias = Union[
    ParametersEvaluationCompareParametersModelAEvaluationModelRequest, str
]


class ParametersEvaluationCompareParametersModelBEvaluationModelRequest(TypedDict, total=False):
    input_template: Required[str]

    max_tokens: Required[int]

    model: Required[str]

    model_source: Required[Literal["serverless", "dedicated", "external"]]

    system_template: Required[str]

    temperature: Required[float]

    external_api_token: str

    external_base_url: str

    num_workers: int


ParametersEvaluationCompareParametersModelB: TypeAlias = Union[
    ParametersEvaluationCompareParametersModelBEvaluationModelRequest, str
]


class ParametersEvaluationCompareParameters(TypedDict, total=False):
    input_data_file_path: Required[str]

    judge: Required[ParametersEvaluationCompareParametersJudge]

    disable_position_bias_correction: bool

    model_a: ParametersEvaluationCompareParametersModelA

    model_b: ParametersEvaluationCompareParametersModelB


Parameters: TypeAlias = Union[
    ParametersEvaluationClassifyParameters, ParametersEvaluationScoreParameters, ParametersEvaluationCompareParameters
]
