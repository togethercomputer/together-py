from __future__ import annotations

import sys
import uuid
from typing import Any, Optional, cast
from typing_extensions import Annotated

from cyclopts import Parameter
from cyclopts.validators import Number as CycloptsNumberValidator

from together import APIError, AsyncClient
from together.types.beta import Endpoint, ShadowSourceParam, ShadowEndpointSourceParam
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfig, CLIConfigParameter
from together.types.beta.endpoints import ShadowExperiment
from together.lib.cli.utils._prompt import PromptParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.endpoints.retrieve import retrieve
from together.types.beta.shadow_endpoint_source_param import (
    Sampling,
    SamplingUniform,
    SamplingKeyBased,
    SamplingAdaptiveUniform,
    SamplingAdaptiveKeyBased,
)
from together.lib.cli.api.beta.endpoints._utils._parameters import ModelPromptParameter, EndpointPromptParameter
from together.lib.cli.api.beta.endpoints._utils._resolve_model import (
    resolve_endpoint,
    construct_model_path,
    resolve_model_and_config,
)
from together.lib.cli.api.beta.endpoints._utils._resolve_config import (
    construct_config_path,
)
from together.lib.cli.api.beta.endpoints._utils._build_autoscaling import build_autoscaling
from together.lib.cli.api.beta.endpoints._utils._find_endpoint_by_deployment import resolve_deployment_id


async def shadow(
    endpoint_or_deployment: Annotated[
        str,
        Parameter(
            name="endpoint",
            help=(
                "Source endpoint (ep_... or name) when creating a new shadow deployment, or an existing "
                "deployment (dep_... or name) to attach as the shadow target"
            ),
        ),
        EndpointPromptParameter(),
    ],
    model: Annotated[
        Optional[str],
        Parameter(
            help="""Model to deploy as the shadow target. Required when ENDPOINT is an endpoint ID/name; omit when
ENDPOINT is an existing deployment. Accepted forms:

- Public model name (for example, zai-org/GLM-5.2).
- Private model name, with or without the project slug.
- Private model ID (ml_...).
- Fully qualified model resource path returned by the API."""
        ),
        ModelPromptParameter(instructions="What model would you like to shadow traffic to?", message="Model"),
    ] = None,
    config_id: Annotated[
        Optional[str],
        Parameter(
            help=(
                "Config revision ID (cr_...) for the shadow deployment. Automatically selected only when one "
                "compatible config exists. Not used when shadowing an existing deployment."
            ),
            name="config",
        ),
    ] = None,
    name: Annotated[
        Optional[str],
        Parameter(
            help=(
                "Shadow deployment name when creating a new deployment (defaults to the model name with a short "
                "suffix); when shadowing an existing deployment, names the shadow target (defaults to "
                "<deployment-name>-target)"
            )
        ),
    ] = None,
    rate: Annotated[
        Optional[float],
        Parameter(
            help="Fixed fraction of live traffic to mirror (0.0–1.0); required unless --target-qps is set",
            validator=CycloptsNumberValidator(gte=0.0, lte=1.0),
        ),
    ] = None,
    key: Annotated[
        Optional[str],
        Parameter(help="Request-body field for sticky key-based sampling"),
    ] = None,
    target_qps: Annotated[
        Optional[float],
        Parameter(
            help="Per-gateway-replica mirrored queries per second (QPS) for adaptive sampling; alternative to --rate"
        ),
    ] = None,
    window: Annotated[
        Optional[str],
        Parameter(help="Observation window for adaptive sampling; applies with --target-qps (default: 60s)"),
    ] = None,
    enable_lora: Annotated[
        bool,
        Parameter(help="Run the multi-LoRA kernel so adapters can be loaded after deployment"),
    ] = False,
    *,
    config: CLIConfigParameter,
) -> None:
    """Mirror sampled live traffic to a shadow deployment without serving its responses.

    Pass an endpoint and MODEL to create a fresh shadow deployment, or pass an existing
    deployment ID (dep_...) as ENDPOINT to attach it as the shadow target. The target stays
    out of live traffic and active rollouts; weight-0 traffic-split warm-up deployments are
    valid shadow targets.
    """
    rate, target_qps = await resolve_rate_or_target_qps(rate, target_qps, config=config)

    sampling = build_sampling(rate=rate, key=key, target_qps=target_qps, window=window)
    source = ShadowSourceParam(endpoint=ShadowEndpointSourceParam(sampling=sampling))
    shadow_name = build_shadow_name(rate, key, target_qps, window)

    existing_deployment = await maybe_resolve_existing_deployment(
        config,
        endpoint_or_deployment,
        model=model,
        config_id=config_id,
        enable_lora=enable_lora,
    )
    if existing_deployment is not None:
        endpoint, resolved_deployment_id = existing_deployment
        endpoint_id = endpoint.id

        # If the shadow experiment already exists, we then just want to add the target to the existing experiment
        # This logic is turned on if the create fails with an error about the experiment already existing
        experiment = await create_or_find_shadow_experiment(config.client, endpoint_id, shadow_name, source)
        assert experiment.id is not None

        deployment = await show_loading_status(
            "Loading shadow deployment...",
            config.client.beta.endpoints.deployments.retrieve(
                id=resolved_deployment_id,
                endpoint_id=endpoint_id,
            ),
        )
        assert deployment.id is not None
        target_name = name if name is not None else f"{deployment.name}-target"

        await show_loading_status(
            "Adding shadow experiment to deployment...",
            config.client.beta.endpoints.shadow_experiments.targets.create(
                endpoint_id=endpoint_id,
                experiment_id=experiment.id,
                name=target_name,
                target_deployment_id=deployment.id,
            ),
        )

        if config.json:
            payload: dict[str, Any] = {"deployment": deployment, "shadow_experiment": experiment}
            console.print_json(openapi_dumps(payload).decode("utf-8"))
            return

        console.print("[green]√[/green] Existing deployment added as shadow target; traffic mirroring started.")
        await retrieve(endpoint_id, config=config)
        return

    model = await resolve_model_for_create(model, config=config)

    endpoint_id = (await resolve_endpoint(config, endpoint_or_deployment)).id
    resolved = await resolve_model_and_config(config, model, config_id=config_id)
    resolved_model, config_value = resolved.model, resolved.config

    autoscaling = build_autoscaling(
        min_replicas=1,
        max_replicas=1,
        scale_up_window=None,
        scale_down_window=None,
        scaling_metrics=None,
        required=True,
    )

    if name is None:
        short_uuid = str(uuid.uuid4())[:8]
        name = f"{resolved_model.name}-{short_uuid}".replace("/", "-")

    # If the shadow experiment already exists, we then just want to add the target to the existing experiment
    # This logic is turned on if the create fails with an error about the experiment already existing
    experiment = await create_or_find_shadow_experiment(config.client, endpoint_id, shadow_name, source)
    assert experiment.id is not None

    deployment = await show_loading_status(
        "Creating shadow deployment...",
        config.client.beta.endpoints.deployments.create(
            endpoint_id=endpoint_id,
            name=name,
            enable_lora=enable_lora,
            model=construct_model_path(resolved_model, resolved.revision_id),
            config=construct_config_path(config_value),
            autoscaling=autoscaling,
        ),
    )

    assert deployment.id is not None

    await show_loading_status(
        "Adding shadow experiment to deployment...",
        config.client.beta.endpoints.shadow_experiments.targets.create(
            endpoint_id=endpoint_id,
            experiment_id=experiment.id,
            name=name + "-target",
            target_deployment_id=deployment.id,
        ),
    )

    if config.json:
        payload = {"deployment": deployment, "shadow_experiment": experiment}
        console.print_json(openapi_dumps(payload).decode("utf-8"))
        return

    console.print("[green]√[/green] Shadow deployment created and traffic mirroring started.")
    await retrieve(endpoint_id, config=config)


async def maybe_resolve_existing_deployment(
    config: CLIConfig,
    endpoint_or_deployment: str,
    *,
    model: str | None,
    config_id: str | None,
    enable_lora: bool,
) -> tuple[Endpoint, str] | None:
    """Return ``(endpoint, deployment_id)`` when the first positional is an existing deployment."""
    explicitly_deployment = endpoint_or_deployment.startswith("dep_")
    explicitly_endpoint = endpoint_or_deployment.startswith("ep_")

    if explicitly_endpoint:
        return None

    if not explicitly_deployment and model is not None:
        # Create path: ENDPOINT + MODEL
        return None

    if not explicitly_deployment and model is None:
        # Ambiguous bare name with no MODEL: only treat as deployment when one uniquely matches.
        # Otherwise fall through to the create path (which will prompt/require MODEL).
        try:
            endpoint, deployment_id = await resolve_deployment_id(config.client, endpoint_or_deployment)
        except ValueError:
            return None
    else:
        endpoint, deployment_id = await resolve_deployment_id(config.client, endpoint_or_deployment)

    if model is not None:
        raise ValueError("Do not pass MODEL when ENDPOINT is an existing deployment.")
    if config_id is not None:
        raise ValueError("Do not pass --config when ENDPOINT is an existing deployment.")
    if enable_lora:
        raise ValueError("Do not pass --enable-lora when ENDPOINT is an existing deployment.")

    return endpoint, deployment_id


async def resolve_model_for_create(
    model: str | None,
    *,
    config: CLIConfig,
) -> str:
    if model is not None:
        return model

    if config.non_interactive:
        raise ValueError("MODEL is required when ENDPOINT is an endpoint ID or name.")

    try:
        prompt = ModelPromptParameter(
            instructions="What model would you like to shadow traffic to?",
            message="Model",
        )
        await prompt.preprompt(config)
        value = await prompt.prompt("model")
        console.print("")
        return cast(str, value)
    except Exception as e:
        raise ValueError("MODEL is required when ENDPOINT is an endpoint ID or name.") from e


async def resolve_rate_or_target_qps(
    rate: float | None,
    target_qps: float | None,
    *,
    config: CLIConfig,
) -> tuple[float | None, float | None]:
    if rate is not None or target_qps is not None:
        return rate, target_qps

    if config.non_interactive:
        raise ValueError("Either rate or target_qps must be provided.")

    try:
        kind = await PromptParameter(
            message="Sampling mode",
            instructions="Shadow needs either a fixed traffic rate or an adaptive QPS target.",
            choices=[
                ("Rate — fixed fraction of live traffic (0.0–1.0)", "rate"),
                ("Target QPS — adaptive per-gateway-replica QPS", "target_qps"),
            ],
        ).prompt("sampling")
        console.print("")

        if kind == "rate":
            raw = await PromptParameter(message="Rate (0.0–1.0)").prompt("rate")
            console.print("")
            value = float(cast(str, raw))
            if not 0.0 <= value <= 1.0:
                raise ValueError("Rate must be between 0.0 and 1.0.")
            return value, None

        raw = await PromptParameter(message="Target QPS").prompt("target_qps")
        console.print("")
        return None, float(cast(str, raw))
    except ValueError:
        raise
    except Exception as e:
        # questionary missing / non-TTY / cancelled → same hard error as non-interactive
        raise ValueError("Either rate or target_qps must be provided.") from e


def build_shadow_name(rate: float | None, key: str | None, target_qps: float | None, window: str | None) -> str:
    rate_value = f"rate-{rate}" if rate is not None else None
    key_value = f"key-{key}" if key is not None else None
    target_qps_value = f"target_qps-{target_qps}" if target_qps is not None else None
    window_value = f"window-{window}" if window is not None else None
    values = ["shadow", rate_value, key_value, target_qps_value, window_value]

    return "-".join(map(lambda x: str(x), filter(lambda x: x is not None, values)))


async def create_or_find_shadow_experiment(
    client: AsyncClient, endpoint_id: str, name: str, source: ShadowSourceParam
) -> ShadowExperiment:
    try:
        return await show_loading_status(
            "Creating shadow experiment...",
            client.beta.endpoints.shadow_experiments.create(
                endpoint_id=endpoint_id,
                name=name,
                source=source,
                targets=[],
            ),
        )
    except APIError as e:
        if "already exists" in e.message.lower():
            async for experiment in client.beta.endpoints.shadow_experiments.list(endpoint_id=endpoint_id):
                if experiment.name == name:
                    return experiment
            raise ValueError(
                f"Shadow experiment {name} not found for endpoint {endpoint_id}. This is likely a bug in the CLI. Please report it to the Together team."
            ) from None
        else:
            raise e from e


def build_sampling(
    *,
    rate: float | None,
    key: str | None,
    target_qps: float | None,
    window: str | None,
) -> Sampling:
    if target_qps is not None:
        if key:
            adaptive: dict[str, Any] = {"key": key, "target_qps": target_qps}
            if window:
                adaptive["window"] = window
            return cast(SamplingAdaptiveKeyBased, {"adaptive_key_based": adaptive})
        adaptive_uniform: dict[str, Any] = {"target_qps": target_qps}
        if window:
            adaptive_uniform["window"] = window
        return cast(SamplingAdaptiveUniform, {"adaptive_uniform": adaptive_uniform})

    if key:
        if rate is None:
            console.print("Error: --rate is required with --key for key-based sampling.")
            sys.exit(1)
        return cast(SamplingKeyBased, {"key_based": {"key": key, "rate": rate}})

    effective_rate = rate if rate is not None else 0.1
    return cast(SamplingUniform, {"uniform": {"rate": effective_rate}})
