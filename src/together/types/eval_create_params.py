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
    """
    Source of the judge model inference: - `serverless`: Together's shared
    serverless inference API. Default concurrency: 25 workers. - `dedicated`: A
    Together dedicated deployment endpoint. Default concurrency: 5 workers (minimum
    enforced even if num_workers is set lower).

    - `external`: An external inference API (e.g. OpenAI, Anthropic, Google,
      OpenRouter). Requires `external_api_token` and `external_base_url`. Default
      concurrency: 2 workers for first-party APIs, 20 for proxy/aggregator
      endpoints.
    """

    system_template: Required[str]
    """System prompt template for the judge"""

    external_api_token: str
    """Bearer/API token for the external judge model provider.

    Required when model_source is 'external'.
    """

    external_base_url: str
    """Base URL of the external inference API for the judge.

    Must be OpenAI-compatible. Required when model_source is 'external'.
    """

    max_tokens: int
    """Maximum number of tokens the judge model may generate.

    Defaults to 32768 if omitted. Set higher for reasoning judges (e.g. o-series,
    Gemini) that spend tokens on internal chain-of-thought before emitting the
    verdict JSON.
    """

    num_workers: int
    """Number of concurrent inference workers for the judge.

    Overrides the source-specific default (serverless: 25, dedicated: 5, external:
    2–20). For dedicated endpoints the value is clamped to a minimum of 5 regardless
    of what is set here.
    """

    temperature: float
    """Sampling temperature for the judge model. Defaults to 0.05 if omitted."""


class ParametersEvaluationClassifyParametersModelToEvaluateEvaluationModelRequest(TypedDict, total=False):
    input_template: Required[str]
    """User message template. Supports Jinja2 variables referencing dataset columns."""

    max_tokens: Required[int]
    """Maximum number of tokens to generate."""

    model: Required[str]
    """Name of the model to evaluate"""

    model_source: Required[Literal["serverless", "dedicated", "external"]]
    """
    Source of the model inference: - `serverless`: Together's shared serverless
    inference API. Default concurrency: 25 workers. - `dedicated`: A Together
    dedicated deployment endpoint. Default concurrency: 5 workers (minimum enforced
    even if num_workers is set lower). Authentication uses the requesting user's
    Together API token automatically.

    - `external`: An external inference API (e.g. OpenAI, Anthropic, Google,
      OpenRouter). Requires `external_api_token` and `external_base_url`. Default
      concurrency: 2 workers for first-party APIs (OpenAI, Anthropic, Google), 20
      for proxy/aggregator endpoints.
    """

    system_template: Required[str]
    """System prompt template. Supports Jinja2 variables referencing dataset columns."""

    temperature: Required[float]
    """Sampling temperature for generation."""

    external_api_token: str
    """Bearer/API token for the external model provider.

    Required when model_source is 'external'.
    """

    external_base_url: str
    """Base URL of the external inference API.

    Must be OpenAI-compatible. Required when model_source is 'external'.
    """

    num_workers: int
    """Number of concurrent inference workers.

    Overrides the source-specific default (serverless: 25, dedicated: 5, external:
    2–20). For dedicated endpoints the value is clamped to a minimum of 5 regardless
    of what is set here.
    """


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
    """Column name in the input dataset containing pre-generated responses"""


class ParametersEvaluationScoreParametersJudge(TypedDict, total=False):
    model: Required[str]
    """Name of the judge model"""

    model_source: Required[Literal["serverless", "dedicated", "external"]]
    """
    Source of the judge model inference: - `serverless`: Together's shared
    serverless inference API. Default concurrency: 25 workers. - `dedicated`: A
    Together dedicated deployment endpoint. Default concurrency: 5 workers (minimum
    enforced even if num_workers is set lower).

    - `external`: An external inference API (e.g. OpenAI, Anthropic, Google,
      OpenRouter). Requires `external_api_token` and `external_base_url`. Default
      concurrency: 2 workers for first-party APIs, 20 for proxy/aggregator
      endpoints.
    """

    system_template: Required[str]
    """System prompt template for the judge"""

    external_api_token: str
    """Bearer/API token for the external judge model provider.

    Required when model_source is 'external'.
    """

    external_base_url: str
    """Base URL of the external inference API for the judge.

    Must be OpenAI-compatible. Required when model_source is 'external'.
    """

    max_tokens: int
    """Maximum number of tokens the judge model may generate.

    Defaults to 32768 if omitted. Set higher for reasoning judges (e.g. o-series,
    Gemini) that spend tokens on internal chain-of-thought before emitting the
    verdict JSON.
    """

    num_workers: int
    """Number of concurrent inference workers for the judge.

    Overrides the source-specific default (serverless: 25, dedicated: 5, external:
    2–20). For dedicated endpoints the value is clamped to a minimum of 5 regardless
    of what is set here.
    """

    temperature: float
    """Sampling temperature for the judge model. Defaults to 0.05 if omitted."""


class ParametersEvaluationScoreParametersModelToEvaluateEvaluationModelRequest(TypedDict, total=False):
    input_template: Required[str]
    """User message template. Supports Jinja2 variables referencing dataset columns."""

    max_tokens: Required[int]
    """Maximum number of tokens to generate."""

    model: Required[str]
    """Name of the model to evaluate"""

    model_source: Required[Literal["serverless", "dedicated", "external"]]
    """
    Source of the model inference: - `serverless`: Together's shared serverless
    inference API. Default concurrency: 25 workers. - `dedicated`: A Together
    dedicated deployment endpoint. Default concurrency: 5 workers (minimum enforced
    even if num_workers is set lower). Authentication uses the requesting user's
    Together API token automatically.

    - `external`: An external inference API (e.g. OpenAI, Anthropic, Google,
      OpenRouter). Requires `external_api_token` and `external_base_url`. Default
      concurrency: 2 workers for first-party APIs (OpenAI, Anthropic, Google), 20
      for proxy/aggregator endpoints.
    """

    system_template: Required[str]
    """System prompt template. Supports Jinja2 variables referencing dataset columns."""

    temperature: Required[float]
    """Sampling temperature for generation."""

    external_api_token: str
    """Bearer/API token for the external model provider.

    Required when model_source is 'external'.
    """

    external_base_url: str
    """Base URL of the external inference API.

    Must be OpenAI-compatible. Required when model_source is 'external'.
    """

    num_workers: int
    """Number of concurrent inference workers.

    Overrides the source-specific default (serverless: 25, dedicated: 5, external:
    2–20). For dedicated endpoints the value is clamped to a minimum of 5 regardless
    of what is set here.
    """


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
    """Column name in the input dataset containing pre-generated responses"""


class ParametersEvaluationCompareParametersJudge(TypedDict, total=False):
    model: Required[str]
    """Name of the judge model"""

    model_source: Required[Literal["serverless", "dedicated", "external"]]
    """
    Source of the judge model inference: - `serverless`: Together's shared
    serverless inference API. Default concurrency: 25 workers. - `dedicated`: A
    Together dedicated deployment endpoint. Default concurrency: 5 workers (minimum
    enforced even if num_workers is set lower).

    - `external`: An external inference API (e.g. OpenAI, Anthropic, Google,
      OpenRouter). Requires `external_api_token` and `external_base_url`. Default
      concurrency: 2 workers for first-party APIs, 20 for proxy/aggregator
      endpoints.
    """

    system_template: Required[str]
    """System prompt template for the judge"""

    external_api_token: str
    """Bearer/API token for the external judge model provider.

    Required when model_source is 'external'.
    """

    external_base_url: str
    """Base URL of the external inference API for the judge.

    Must be OpenAI-compatible. Required when model_source is 'external'.
    """

    max_tokens: int
    """Maximum number of tokens the judge model may generate.

    Defaults to 32768 if omitted. Set higher for reasoning judges (e.g. o-series,
    Gemini) that spend tokens on internal chain-of-thought before emitting the
    verdict JSON.
    """

    num_workers: int
    """Number of concurrent inference workers for the judge.

    Overrides the source-specific default (serverless: 25, dedicated: 5, external:
    2–20). For dedicated endpoints the value is clamped to a minimum of 5 regardless
    of what is set here.
    """

    temperature: float
    """Sampling temperature for the judge model. Defaults to 0.05 if omitted."""


class ParametersEvaluationCompareParametersModelAEvaluationModelRequest(TypedDict, total=False):
    input_template: Required[str]
    """User message template. Supports Jinja2 variables referencing dataset columns."""

    max_tokens: Required[int]
    """Maximum number of tokens to generate."""

    model: Required[str]
    """Name of the model to evaluate"""

    model_source: Required[Literal["serverless", "dedicated", "external"]]
    """
    Source of the model inference: - `serverless`: Together's shared serverless
    inference API. Default concurrency: 25 workers. - `dedicated`: A Together
    dedicated deployment endpoint. Default concurrency: 5 workers (minimum enforced
    even if num_workers is set lower). Authentication uses the requesting user's
    Together API token automatically.

    - `external`: An external inference API (e.g. OpenAI, Anthropic, Google,
      OpenRouter). Requires `external_api_token` and `external_base_url`. Default
      concurrency: 2 workers for first-party APIs (OpenAI, Anthropic, Google), 20
      for proxy/aggregator endpoints.
    """

    system_template: Required[str]
    """System prompt template. Supports Jinja2 variables referencing dataset columns."""

    temperature: Required[float]
    """Sampling temperature for generation."""

    external_api_token: str
    """Bearer/API token for the external model provider.

    Required when model_source is 'external'.
    """

    external_base_url: str
    """Base URL of the external inference API.

    Must be OpenAI-compatible. Required when model_source is 'external'.
    """

    num_workers: int
    """Number of concurrent inference workers.

    Overrides the source-specific default (serverless: 25, dedicated: 5, external:
    2–20). For dedicated endpoints the value is clamped to a minimum of 5 regardless
    of what is set here.
    """


ParametersEvaluationCompareParametersModelA: TypeAlias = Union[
    ParametersEvaluationCompareParametersModelAEvaluationModelRequest, str
]


class ParametersEvaluationCompareParametersModelBEvaluationModelRequest(TypedDict, total=False):
    input_template: Required[str]
    """User message template. Supports Jinja2 variables referencing dataset columns."""

    max_tokens: Required[int]
    """Maximum number of tokens to generate."""

    model: Required[str]
    """Name of the model to evaluate"""

    model_source: Required[Literal["serverless", "dedicated", "external"]]
    """
    Source of the model inference: - `serverless`: Together's shared serverless
    inference API. Default concurrency: 25 workers. - `dedicated`: A Together
    dedicated deployment endpoint. Default concurrency: 5 workers (minimum enforced
    even if num_workers is set lower). Authentication uses the requesting user's
    Together API token automatically.

    - `external`: An external inference API (e.g. OpenAI, Anthropic, Google,
      OpenRouter). Requires `external_api_token` and `external_base_url`. Default
      concurrency: 2 workers for first-party APIs (OpenAI, Anthropic, Google), 20
      for proxy/aggregator endpoints.
    """

    system_template: Required[str]
    """System prompt template. Supports Jinja2 variables referencing dataset columns."""

    temperature: Required[float]
    """Sampling temperature for generation."""

    external_api_token: str
    """Bearer/API token for the external model provider.

    Required when model_source is 'external'.
    """

    external_base_url: str
    """Base URL of the external inference API.

    Must be OpenAI-compatible. Required when model_source is 'external'.
    """

    num_workers: int
    """Number of concurrent inference workers.

    Overrides the source-specific default (serverless: 25, dedicated: 5, external:
    2–20). For dedicated endpoints the value is clamped to a minimum of 5 regardless
    of what is set here.
    """


ParametersEvaluationCompareParametersModelB: TypeAlias = Union[
    ParametersEvaluationCompareParametersModelBEvaluationModelRequest, str
]


class ParametersEvaluationCompareParameters(TypedDict, total=False):
    input_data_file_path: Required[str]
    """Data file ID"""

    judge: Required[ParametersEvaluationCompareParametersJudge]

    disable_position_bias_correction: bool
    """
    When false (default), the judge runs twice per sample: once with model A's
    response first (original order) and once with model B's response first (flipped
    order). The two verdicts are reconciled to cancel out position bias. When true,
    only the original-order pass is run, halving judge cost and latency at the
    expense of position-bias correction. The result file will not contain
    flipped-order judge fields when this is true.
    """

    model_a: ParametersEvaluationCompareParametersModelA
    """
    Either an EvaluationModelRequest for generation or a string column name from the
    dataset (when responses are pre-generated). When both model_a and model_b are
    EvaluationModelRequest objects, their inference runs execute in parallel to
    reduce total wall-clock time.
    """

    model_b: ParametersEvaluationCompareParametersModelB
    """
    Either an EvaluationModelRequest for generation or a string column name from the
    dataset (when responses are pre-generated). When both model_a and model_b are
    EvaluationModelRequest objects, their inference runs execute in parallel to
    reduce total wall-clock time.
    """


Parameters: TypeAlias = Union[
    ParametersEvaluationClassifyParameters, ParametersEvaluationScoreParameters, ParametersEvaluationCompareParameters
]
