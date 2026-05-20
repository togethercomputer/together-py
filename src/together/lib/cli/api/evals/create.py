from __future__ import annotations

from typing import Any, Dict, Union, Literal, Optional, Annotated, cast
from pathlib import Path

from cyclopts import Parameter

from together import TogetherError
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
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
    type_: Annotated[
        Literal["classify", "score", "compare"], Parameter(name="type", help="The type of evaluation to create")
    ],
    judge_model: Annotated[str, Parameter(help="Name or URL of the judge model to use for evaluation")],
    judge_model_source: Annotated[
        Literal["serverless", "dedicated", "external"], Parameter(help="Source of the judge model")
    ],
    judge_system_template: Annotated[str, Parameter(help="System template for the judge model")],
    input_data_file_path: Annotated[str, Parameter(help="The path to the input data file")],
    judge_external_api_token: Annotated[
        Optional[str], Parameter(help="API token for access to the external judge model")
    ] = None,
    judge_external_base_url: Annotated[
        Optional[str], Parameter(help="Base URL for access to the external judge model")
    ] = None,
    model_field: Annotated[
        Optional[str],
        Parameter(
            help="Name of the field in the input file containing model-generated text; mutually exclusive with --model-to-evaluate and other model config flags"
        ),
    ] = None,
    model_to_evaluate: Annotated[Optional[str], Parameter(help="Model name when using the detailed config")] = None,
    model_to_evaluate_source: Annotated[
        Optional[Literal["serverless", "dedicated", "external"]], Parameter(help="Source of the model to evaluate")
    ] = None,
    model_to_evaluate_external_api_token: Annotated[
        Optional[str], Parameter(help="API token for access to the external model to evaluate")
    ] = None,
    model_to_evaluate_external_base_url: Annotated[
        Optional[str], Parameter(help="Base URL for access to the external model to evaluate")
    ] = None,
    model_to_evaluate_max_tokens: Annotated[
        Optional[int], Parameter(help="Max tokens for the model to evaluate")
    ] = None,
    model_to_evaluate_temperature: Annotated[
        Optional[float], Parameter(help="Temperature for the model to evaluate")
    ] = None,
    model_to_evaluate_system_template: Annotated[
        Optional[str], Parameter(help="System template for the model to evaluate")
    ] = None,
    model_to_evaluate_input_template: Annotated[
        Optional[str], Parameter(help="Input template for the model to evaluate")
    ] = None,
    labels: Annotated[Optional[str], Parameter(help="Classify labels - comma-separated list")] = None,
    pass_labels: Annotated[
        Optional[str],
        Parameter(help="Comma-separated list of labels considered as passing (required for classify type)"),
    ] = None,
    min_score: Annotated[Optional[float], Parameter(help="Minimum score value (required for score type)")] = None,
    max_score: Annotated[Optional[float], Parameter(help="Maximum score value (required for score type)")] = None,
    pass_threshold: Annotated[
        Optional[float], Parameter(help="Threshold for passing (required for score type)")
    ] = None,
    disable_position_bias_correction: Annotated[
        bool,
        Parameter(
            negative=(),
            help="For compare evals, run only the original-order judge pass without position-bias correction",
        ),
    ] = False,
    model_a_field: Annotated[
        Optional[str],
        Parameter(
            help="Name of the field in the input file containing Model A's generated text; mutually exclusive with --model-a and other Model A config flags"
        ),
    ] = None,
    model_a: Annotated[
        Optional[str], Parameter(help="Model name or URL for model A when using detailed config")
    ] = None,
    model_a_source: Annotated[
        Optional[Literal["serverless", "dedicated", "external"]], Parameter(help="Source of model A")
    ] = None,
    model_a_external_api_token: Annotated[
        Optional[str], Parameter(help="API token for access to external model A")
    ] = None,
    model_a_external_base_url: Annotated[
        Optional[str], Parameter(help="Base URL for access to external model A")
    ] = None,
    model_a_max_tokens: Annotated[Optional[int], Parameter(help="Max tokens for model A")] = None,
    model_a_temperature: Annotated[Optional[float], Parameter(help="Temperature for model A")] = None,
    model_a_system_template: Annotated[Optional[str], Parameter(help="System template for model A")] = None,
    model_a_input_template: Annotated[Optional[str], Parameter(help="Input template for model A")] = None,
    model_b_field: Annotated[
        Optional[str],
        Parameter(
            help="Name of the field in the input file containing Model B's generated text; mutually exclusive with --model-b and other Model B config flags"
        ),
    ] = None,
    model_b: Annotated[
        Optional[str], Parameter(help="Model name or URL for model B when using detailed config")
    ] = None,
    model_b_source: Annotated[
        Optional[Literal["serverless", "dedicated", "external"]], Parameter(help="Source of model B")
    ] = None,
    model_b_external_api_token: Annotated[
        Optional[str], Parameter(help="API token for access to external model B")
    ] = None,
    model_b_external_base_url: Annotated[
        Optional[str], Parameter(help="Base URL for access to external model B")
    ] = None,
    model_b_max_tokens: Annotated[Optional[int], Parameter(help="Max tokens for model B")] = None,
    model_b_temperature: Annotated[Optional[float], Parameter(help="Temperature for model B")] = None,
    model_b_system_template: Annotated[Optional[str], Parameter(help="System template for model B")] = None,
    model_b_input_template: Annotated[Optional[str], Parameter(help="Input template for model B")] = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """Create a new evaluation job."""
    type_val = type_

    labels_list = labels.split(",") if labels else None
    pass_labels_list = pass_labels.split(",") if pass_labels else None

    # If the user passes a path to a file, try to upload it to the files API first
    # Uploads are idempotent so we can depend on this API always giving us a file ID
    if _check_path_exists(input_data_file_path):
        file_upload = await config.client.files.upload(Path(input_data_file_path), purpose="eval", check=False)
        training_file = file_upload.id
    else:
        training_file = input_data_file_path

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
            "max_tokens": model_to_evaluate_max_tokens if model_to_evaluate_max_tokens is not None else 16000,
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
            "max_tokens": model_a_max_tokens if model_a_max_tokens is not None else 16000,
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
            "max_tokens": model_b_max_tokens if model_b_max_tokens is not None else 16000,
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
                input_data_file_path=training_file,
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
                input_data_file_path=training_file,
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
                input_data_file_path=training_file,
                judge=judge_config,
                disable_position_bias_correction=disable_position_bias_correction,
                model_a=cast(ParametersEvaluationCompareParametersModelAEvaluationModelRequest, model_a_final),
                model_b=cast(ParametersEvaluationCompareParametersModelBEvaluationModelRequest, model_b_final),
            ),
        )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
    else:
        url = f"https://api.together.ai/evaluations/result/{response.workflow_id}"
        console.print(f"[green]√ Evaluation job created[/green] [dim]([link={url}]{response.workflow_id}[/link])[/dim]")
        console.print(f"  Evaluations may take some time to complete.\n")
        console.print(f"  To retrieve the status:")
        console.print(f"    [dim]-[/dim] [primary]tg evals status {response.workflow_id}[/primary]")
        console.print(f"  To get the results:")
        console.print(f"    [dim]-[/dim] [primary]tg evals {response.workflow_id}[/primary]")


def _build_judge(
    type_val: Literal["classify", "score", "compare"],
    judge_model: str,
    judge_model_source: Literal["serverless", "dedicated", "external"],
    judge_system_template: str,
    judge_external_api_token: Optional[str],
    judge_external_base_url: Optional[str],
) -> (
    ParametersEvaluationClassifyParametersJudge
    | ParametersEvaluationScoreParametersJudge
    | ParametersEvaluationCompareParametersJudge
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


def _check_path_exists(path_string: str) -> bool:
    if path_string == "":
        return False
    p = Path(path_string)
    if p.is_dir():
        raise ValueError(f"Path {path_string} is a directory, not a file. Please provide a file path.")
    return p.exists() and p.is_file()
