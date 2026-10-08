from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.training.prepare_for_fp4_inference._utils import (
    AdapterRevisionParameter,
    CalibrationFileParameter,
    build_inputs,
    format_estimate,
    format_credit_warning,
    resolve_calibration_file,
)


async def estimate(
    adapter_object_id: Annotated[str, Parameter(help="Model object ID of the fine-tuned adapter to prepare")],
    *,
    adapter_revision_id: AdapterRevisionParameter = None,
    calibration_file: CalibrationFileParameter = None,
    config: CLIConfigParameter,
) -> None:
    """Estimate the price and duration of preparing an adapter for FP4 inference."""
    calibration_file_id = await resolve_calibration_file(calibration_file, config)
    inputs = build_inputs(adapter_object_id, adapter_revision_id, calibration_file_id)
    response = await show_loading_status(
        "Estimating price...",
        config.client.post_training.prepare_for_fp4_inference.estimate_cost(inputs=inputs),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print(format_estimate(response))
    if not response.allowed_to_proceed:
        console.print(format_credit_warning(response))
