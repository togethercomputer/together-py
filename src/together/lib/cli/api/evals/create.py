from __future__ import annotations

import json
from typing import Any, Dict, Union, Literal, Optional, Annotated, cast

from rich import print, print_json
from cyclopts import Parameter

from together import TogetherError
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfig
from together.types.eval_create_params import (
    ParametersEvaluationScoreParameters,
    ParametersEvaluationCompareParameters,
    ParametersEvaluationClassifyParameters,
    ParametersEvaluationScoreParametersJudge,
    ParametersEvaluationCompareParametersJudge,
    ParametersEvaluationClassifyParametersJudge,
    ParametersEvaluationScoreParametersModelToEvaluate,
    ParametersEvaluationClassifyParametersModelToEvaluate,
    ParametersEvaluationCompareParametersModelAEvaluationModelRequest,
    ParametersEvaluationCompareParametersModelBEvaluationModelRequest,
)


async def create(
    type_: Literal["classify", "score", "compare"],
    judge_model: str,
    judge_model_source: Literal["serverless", "dedicated", "external"],
    judge_system_template: str,
    input_data_file_path: str,
    judge_external_api_token: Optional[str] = None,
    judge_external_base_url: Optional[str] = None,
    model_field: Optional[str] = None,
    model_to_evaluate: Optional[str] = None,
    model_to_evaluate_source: Optional[Literal["serverless", "dedicated", "external"]] = None,
    model_to_evaluate_external_api_token: Optional[str] = None,
    model_to_evaluate_external_base_url: Optional[str] = None,
    model_to_evaluate_max_tokens: Optional[int] = None,
    model_to_evaluate_temperature: Optional[float] = None,
    model_to_evaluate_system_template: Optional[str] = None,
    model_to_evaluate_input_template: Optional[str] = None,
    labels: Optional[str] = None,
    pass_labels: Optional[str] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    pass_threshold: Optional[float] = None,
    model_a_field: Optional[str] = None,
    model_a: Optional[str] = None,
    model_a_source: Optional[Literal["serverless", "dedicated", "external"]] = None,
    model_a_external_api_token: Optional[str] = None,
    model_a_external_base_url: Optional[str] = None,
    model_a_max_tokens: Optional[int] = None,
    model_a_temperature: Optional[float] = None,
    model_a_system_template: Optional[str] = None,
    model_a_input_template: Optional[str] = None,
    model_b_field: Optional[str] = None,
    model_b: Optional[str] = None,
    model_b_source: Optional[Literal["serverless", "dedicated", "external"]] = None,
    model_b_external_api_token: Optional[str] = None,
    model_b_external_base_url: Optional[str] = None,
    model_b_max_tokens: Optional[int] = None,
    model_b_temperature: Optional[float] = None,
    model_b_system_template: Optional[str] = None,
    model_b_input_template: Optional[str] = None,
    *,
    config: Annotated[CLIConfig, Parameter(parse=False)],
) -> None:
    """Create a new evaluation job."""
    type_val = type_

    labels_list = labels.split(",") if labels else None
    pass_labels_list = pass_labels.split(",") if pass_labels else None

    model_to_evaluate_final: Union[Dict[str, Any], None, str] = None
    config_params_provided = any(
        [
            model_to_evaluate,
            model_to_evaluate_source,
            model_to_evaluate_max_tokens,
            model_to_evaluate_temperature,
            model_to_evaluate_system_template,
            model_to_evaluate_input_template,
        ]
    )

    if model_field:
        if config_params_provided:
            raise ValueError(
                "Cannot specify both --model-field and --model-to-evaluate-* parameters. "
                "Use either --model-field alone if your input file has pre-generated responses, "
                "or config parameters if you want to generate it on our end"
            )
        model_to_evaluate_final = model_field
    elif config_params_provided:
        model_to_evaluate_final = {
            "model": model_to_evaluate,
            "model_source": model_to_evaluate_source,
            "max_tokens": model_to_evaluate_max_tokens,
            "temperature": model_to_evaluate_temperature,
            "system_template": model_to_evaluate_system_template,
            "input_template": model_to_evaluate_input_template,
        }
        if model_to_evaluate_external_api_token:
            model_to_evaluate_final["external_api_token"] = model_to_evaluate_external_api_token
        if model_to_evaluate_external_base_url:
            model_to_evaluate_final["external_base_url"] = model_to_evaluate_external_base_url

    model_a_final: Union[Dict[str, Any], None, str] = None
    model_a_config_params = [
        model_a,
        model_a_source,
        model_a_max_tokens,
        model_a_temperature,
        model_a_system_template,
        model_a_input_template,
    ]
    if model_a_field is not None:
        if any(model_a_config_params):
            raise ValueError(
                "Cannot specify both --model-a-field and config parameters (--model-a-name, etc.). "
                "Use either --model-a-field alone if your input file has pre-generated responses, "
                "or config parameters if you want to generate it on our end"
            )
        model_a_final = model_a_field
    elif any(model_a_config_params):
        model_a_final = {
            "model": model_a,
            "model_source": model_a_source,
            "max_tokens": model_a_max_tokens,
            "temperature": model_a_temperature,
            "system_template": model_a_system_template,
            "input_template": model_a_input_template,
        }
        if model_a_external_api_token:
            model_a_final["external_api_token"] = model_a_external_api_token
        if model_a_external_base_url:
            model_a_final["external_base_url"] = model_a_external_base_url

    model_b_final: Union[Dict[str, Any], None, str] = None
    model_b_config_params = [
        model_b,
        model_b_source,
        model_b_max_tokens,
        model_b_temperature,
        model_b_system_template,
        model_b_input_template,
    ]
    if model_b_field is not None:
        if any(model_b_config_params):
            raise ValueError(
                "Cannot specify both --model-b-field and config parameters (--model-b-name, etc.). "
                "Use either --model-b-field alone if your input file has pre-generated responses, "
                "or config parameters if you want to generate it on our end"
            )
        model_b_final = model_b_field
    elif any(model_b_config_params):
        model_b_final = {
            "model": model_b,
            "model_source": model_b_source,
            "max_tokens": model_b_max_tokens,
            "temperature": model_b_temperature,
            "system_template": model_b_system_template,
            "input_template": model_b_input_template,
        }
        if model_b_external_api_token:
            model_b_final["external_api_token"] = model_b_external_api_token
        if model_b_external_base_url:
            model_b_final["external_base_url"] = model_b_external_base_url

    judge_config = _build_judge(
        type_val,
        judge_model,
        judge_model_source,
        judge_system_template,
        judge_external_api_token,
        judge_external_base_url,
    )

    if type_val == "classify":
        response = await config.client.evals.create(
            type=type_val,
            parameters=ParametersEvaluationClassifyParameters(
                input_data_file_path=input_data_file_path,
                judge=judge_config,
                labels=labels_list or [],
                pass_labels=pass_labels_list or [],
                model_to_evaluate=cast(ParametersEvaluationClassifyParametersModelToEvaluate, model_to_evaluate_final),
            ),
        )
    elif type_val == "score":
        if max_score is None or min_score is None or pass_threshold is None:
            raise TogetherError("max_score, min_score, and pass_threshold are required for score type")
        response = await config.client.evals.create(
            type="score",
            parameters=ParametersEvaluationScoreParameters(
                input_data_file_path=input_data_file_path,
                judge=judge_config,
                max_score=max_score,
                min_score=min_score,
                pass_threshold=pass_threshold,
                model_to_evaluate=cast(ParametersEvaluationScoreParametersModelToEvaluate, model_to_evaluate_final),
            ),
        )
    else:
        response = await config.client.evals.create(
            type=type_val,
            parameters=ParametersEvaluationCompareParameters(
                input_data_file_path=input_data_file_path,
                judge=judge_config,
                model_a=cast(ParametersEvaluationCompareParametersModelAEvaluationModelRequest, model_a_final),
                model_b=cast(ParametersEvaluationCompareParametersModelBEvaluationModelRequest, model_b_final),
            ),
        )

    if config.json:
        print_json(openapi_dumps(response).decode("utf-8"))
    else:
        print(json.dumps(response.model_dump(exclude_none=True), indent=4))


def _build_judge(
    type_val: Literal["classify", "score", "compare"],
    judge_model: str,
    judge_model_source: Literal["serverless", "dedicated", "external"],
    judge_system_template: str,
    judge_external_api_token: Optional[str],
    judge_external_base_url: Optional[str],
):
    if type_val == "classify":
        judge_config = ParametersEvaluationClassifyParametersJudge(
            model=judge_model,
            model_source=judge_model_source,
            system_template=judge_system_template,
        )
    elif type_val == "score":
        judge_config = ParametersEvaluationScoreParametersJudge(
            model=judge_model,
            model_source=judge_model_source,
            system_template=judge_system_template,
        )
    else:
        judge_config = ParametersEvaluationCompareParametersJudge(
            model=judge_model,
            model_source=judge_model_source,
            system_template=judge_system_template,
        )
    if judge_external_api_token:
        judge_config["external_api_token"] = judge_external_api_token
    if judge_external_base_url:
        judge_config["external_base_url"] = judge_external_base_url
    return judge_config
