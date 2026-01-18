from __future__ import annotations

from typing import Any, Literal

import click
from rich import print as rprint
from click.core import ParameterSource

from together import Together
from together.types import fine_tuning_estimate_price_params as pe_params
from together.lib.utils import log_warn
from together.lib.cli.api._utils import INT_WITH_MAX, BOOL_WITH_AUTO, handle_api_errors
from together.lib.resources.fine_tuning import get_model_limits

_CONFIRMATION_MESSAGE = (
    "You are about to create a fine-tuning job. "
    "The estimated price of this job is {price}. "
    "The actual cost of your job will be determined by the model size, the number of tokens "
    "in the training file, the number of tokens in the validation file, the number of epochs, and "
    "the number of evaluations. Visit https://www.together.ai/pricing to learn more about pricing.\n"
    "{warning}"
    "You can pass `-y` or `--confirm` to your command to skip this message.\n\n"
    "Do you want to proceed?"
)

_WARNING_MESSAGE_INSUFFICIENT_FUNDS = (
    "The estimated price of this job is significantly greater than your current credit limit and balance combined. "
    "It will likely get cancelled due to insufficient funds. "
    "Consider increasing your credit limit at https://api.together.xyz/settings/profile\n"
)


@click.command()
@click.pass_context
@click.option(
    "--training-file",
    "-t",
    type=str,
    required=True,
    help="Training file ID from Files API",
)
@click.option("--model", "-m", type=str, help="Base model name")
@click.option("--n-epochs", "-ne", type=int, default=1, help="Number of epochs to train for")
@click.option("--validation-file", type=str, default="", help="Validation file ID from Files API")
@click.option("--n-evals", type=int, default=0, help="Number of evaluation loops")
@click.option("--n-checkpoints", "-c", type=int, default=1, help="Number of checkpoints to save")
@click.option("--batch-size", "-b", type=INT_WITH_MAX, default="max", help="Train batch size")
@click.option("--learning-rate", "-lr", type=float, default=1e-5, help="Learning rate")
@click.option(
    "--lr-scheduler-type",
    type=click.Choice(["linear", "cosine"]),
    default="cosine",
    help="Learning rate scheduler type",
)
@click.option(
    "--min-lr-ratio",
    type=float,
    default=0.0,
    help="The ratio of the final learning rate to the peak learning rate",
)
@click.option(
    "--scheduler-num-cycles",
    type=float,
    default=0.5,
    help="Number or fraction of cycles for the cosine learning rate scheduler.",
)
@click.option(
    "--warmup-ratio",
    type=float,
    default=0.0,
    help="Warmup ratio for the learning rate scheduler.",
)
@click.option(
    "--max-grad-norm",
    type=float,
    default=1.0,
    help="Max gradient norm to be used for gradient clipping. Set to 0 to disable.",
)
@click.option(
    "--weight-decay",
    type=float,
    default=0.0,
    help="Weight decay",
)
@click.option(
    "--lora/--no-lora",
    type=bool,
    default=True,
    help="Whether to use LoRA adapters for fine-tuning",
)
@click.option("--lora-r", type=int, default=8, help="LoRA adapters' rank")
@click.option("--lora-dropout", type=float, default=0, help="LoRA adapters' dropout")
@click.option("--lora-alpha", type=float, default=8, help="LoRA adapters' alpha")
@click.option(
    "--lora-trainable-modules",
    type=str,
    default="all-linear",
    help="Trainable modules for LoRA adapters. For example, 'all-linear', 'q_proj,v_proj'",
)
@click.option(
    "--training-method",
    type=click.Choice(["sft", "dpo"]),
    default="sft",
    help="Training method to use. Options: sft (supervised fine-tuning), dpo (Direct Preference Optimization)",
)
@click.option(
    "--dpo-beta",
    type=float,
    default=None,
    help="Beta parameter for DPO training (only used when '--training-method' is 'dpo')",
)
@click.option(
    "--dpo-normalize-logratios-by-length",
    type=bool,
    default=False,
    help=("Whether to normalize logratios by sample length (only used when '--training-method' is 'dpo')"),
)
@click.option(
    "--rpo-alpha",
    type=float,
    default=None,
    help=(
        "RPO alpha parameter of DPO training to include NLL in the loss (only used when '--training-method' is 'dpo')"
    ),
)
@click.option(
    "--simpo-gamma",
    type=float,
    default=None,
    help="SimPO gamma parameter (only used when '--training-method' is 'dpo')",
)
@click.option(
    "--suffix",
    "-s",
    type=str,
    default=None,
    help="Suffix for the fine-tuned model name",
)
@click.option("--wandb-api-key", type=str, default=None, help="Wandb API key")
@click.option("--wandb-base-url", type=str, default=None, help="Wandb base URL")
@click.option("--wandb-project-name", type=str, default=None, help="Wandb project name")
@click.option("--wandb-name", type=str, default=None, help="Wandb run name")
@click.option(
    "--confirm",
    "-y",
    type=bool,
    is_flag=True,
    default=False,
    help="Whether to skip the launch confirmation message",
)
@click.option(
    "--train-on-inputs",
    type=BOOL_WITH_AUTO,
    default=None,
    help="Whether to mask the user messages in conversational data or prompts in instruction data. "
    "`auto` will automatically determine whether to mask the inputs based on the data format.",
)
@click.option(
    "--train-vision",
    type=bool,
    default=False,
    help="Whether to train the vision encoder. Only supported for multimodal models.",
)
@click.option(
    "--from-checkpoint",
    type=str,
    default=None,
    help="The checkpoint identifier to continue training from a previous fine-tuning job. "
    "The format: {$JOB_ID/$OUTPUT_MODEL_NAME}:{$STEP}. "
    "The step value is optional, without it the final checkpoint will be used.",
)
@click.option(
    "--from-hf-model",
    type=str,
    help="The Hugging Face Hub repo to start training from. "
    "Should be as close as possible to the base model (specified by the `model` argument) "
    "in terms of architecture and size",
)
@click.option(
    "--hf-model-revision",
    type=str,
    help="The revision of the Hugging Face Hub model to continue training from. "
    "Example: hf_model_revision=None (defaults to the latest revision in `main`) "
    "or hf_model_revision='607a30d783dfa663caf39e06633721c8d4cfcd7e' (specific commit).",
)
@click.option(
    "--hf-api-token",
    type=str,
    default=None,
    help="HF API token to use for uploading a checkpoint to a private repo",
)
@click.option(
    "--hf-output-repo-name",
    type=str,
    default=None,
    help="HF repo to upload the fine-tuned model to",
)
@handle_api_errors("Fine-tuning")
def create(
    ctx: click.Context,
    training_file: str,
    validation_file: str,
    model: str | None,
    n_epochs: int,
    n_evals: int,
    n_checkpoints: int,
    batch_size: int | Literal["max"],
    learning_rate: float,
    lr_scheduler_type: Literal["linear", "cosine"],
    min_lr_ratio: float,
    scheduler_num_cycles: float,
    warmup_ratio: float,
    max_grad_norm: float,
    weight_decay: float,
    lora: bool | None,
    lora_r: int | None,
    lora_dropout: float | None,
    lora_alpha: float | None,
    lora_trainable_modules: str | None,
    train_vision: bool,
    suffix: str | None,
    wandb_api_key: str | None,
    wandb_base_url: str | None,
    wandb_project_name: str | None,
    wandb_name: str | None,
    confirm: bool | None,
    train_on_inputs: bool | Literal["auto"] | None,
    training_method: str | None,
    dpo_beta: float | None,
    dpo_normalize_logratios_by_length: bool | None,
    rpo_alpha: float | None,
    simpo_gamma: float | None,
    from_checkpoint: str | None,
    from_hf_model: str | None,
    hf_model_revision: str | None,
    hf_api_token: str | None,
    hf_output_repo_name: str | None,
) -> None:
    """Start fine-tuning"""
    client: Together = ctx.obj

    training_args: dict[str, Any] = dict(
        training_file=training_file,
        model=model,
        n_epochs=n_epochs,
        validation_file=validation_file,
        n_evals=n_evals,
        n_checkpoints=n_checkpoints,
        batch_size=batch_size,
        learning_rate=learning_rate,
        lr_scheduler_type=lr_scheduler_type,
        min_lr_ratio=min_lr_ratio,
        scheduler_num_cycles=scheduler_num_cycles,
        warmup_ratio=warmup_ratio,
        max_grad_norm=max_grad_norm,
        weight_decay=weight_decay,
        lora=lora,
        lora_r=lora_r,
        lora_dropout=lora_dropout,
        lora_alpha=lora_alpha,
        lora_trainable_modules=lora_trainable_modules,
        train_vision=train_vision,
        suffix=suffix,
        wandb_api_key=wandb_api_key,
        wandb_base_url=wandb_base_url,
        wandb_project_name=wandb_project_name,
        wandb_name=wandb_name,
        train_on_inputs=train_on_inputs,
        training_method=training_method,
        dpo_beta=dpo_beta,
        dpo_normalize_logratios_by_length=dpo_normalize_logratios_by_length,
        rpo_alpha=rpo_alpha,
        simpo_gamma=simpo_gamma,
        from_checkpoint=from_checkpoint,
        from_hf_model=from_hf_model,
        hf_model_revision=hf_model_revision,
        hf_api_token=hf_api_token,
        hf_output_repo_name=hf_output_repo_name,
    )

    if model is None and from_checkpoint is None:
        raise click.BadParameter("You must specify either a model or a checkpoint")

    model_name = model
    if from_checkpoint is not None:
        model_name = from_checkpoint.split(":")[0]

    model_limits = get_model_limits(client, str(model_name))

    if lora:
        if model_limits.lora_training is None:
            raise click.BadParameter(f"LoRA fine-tuning is not supported for the model `{model}`")
        default_values = {
            "lora_r": model_limits.lora_training.max_rank,
            "learning_rate": 1e-3,
        }

        for arg in default_values:
            arg_source = ctx.get_parameter_source("arg")  # type: ignore[attr-defined]
            if arg_source == ParameterSource.DEFAULT:
                training_args[arg] = default_values[str(arg_source)]

        if ctx.get_parameter_source("lora_alpha") == ParameterSource.DEFAULT:  # type: ignore[attr-defined]
            training_args["lora_alpha"] = training_args["lora_r"] * 2
    else:
        if model_limits.full_training is None:
            raise click.BadParameter(f"Full fine-tuning is not supported for the model `{model}`")

        for param in ["lora_r", "lora_dropout", "lora_alpha", "lora_trainable_modules"]:
            param_source = ctx.get_parameter_source(param)  # type: ignore[attr-defined]
            if param_source != ParameterSource.DEFAULT:
                raise click.BadParameter(
                    f"You set LoRA parameter `{param}` for a full fine-tuning job. "
                    f"Please change the job type with --lora or remove `{param}` from the arguments"
                )

    if n_evals <= 0 and validation_file:
        log_warn(
            "Warning: You have specified a validation file but the number of evaluation loops is set to 0. No evaluations will be performed."
        )
    elif n_evals > 0 and not validation_file:
        raise click.BadParameter("You have specified a number of evaluation loops but no validation file.")

    training_type_cls: pe_params.TrainingType
    if lora:
        training_type_cls = pe_params.TrainingTypeLoRaTrainingType(
            lora_alpha=int(lora_alpha or 0),
            lora_r=lora_r or 0,
            lora_dropout=lora_dropout or 0,
            lora_trainable_modules=lora_trainable_modules or "all-linear",
            type="Lora",
        )
    else:
        training_type_cls = pe_params.TrainingTypeFullTrainingType(
            type="Full",
        )

    training_method_cls: pe_params.TrainingMethod
    if training_method == "sft":
        training_method_cls = pe_params.TrainingMethodTrainingMethodSft(
            method="sft",
            train_on_inputs=train_on_inputs or "auto",
        )
    else:
        training_method_cls = pe_params.TrainingMethodTrainingMethodDpo(
            method="dpo",
            dpo_beta=dpo_beta or 0,
            dpo_normalize_logratios_by_length=dpo_normalize_logratios_by_length or False,
            dpo_reference_free=False,
            rpo_alpha=rpo_alpha or 0,
            simpo_gamma=simpo_gamma or 0,
        )

    if model_limits.supports_vision:
        # Don't show price estimation for multimodal models yet
        confirm = True

    finetune_price_estimation_result = client.fine_tuning.estimate_price(
        training_file=training_file,
        validation_file=validation_file,
        model=model or "",
        n_epochs=n_epochs,
        n_evals=n_evals,
        training_type=training_type_cls,
        training_method=training_method_cls,
    )
    price = click.style(
        f"${finetune_price_estimation_result.estimated_total_price:.2f}",
        bold=True,
    )
    if not finetune_price_estimation_result.allowed_to_proceed:
        warning = click.style(_WARNING_MESSAGE_INSUFFICIENT_FUNDS, fg="red", bold=True)
    else:
        warning = ""

    confirmation_message = _CONFIRMATION_MESSAGE.format(
        price=price,
        warning=warning,
    )

    if confirm or click.confirm(confirmation_message, default=True, show_default=True):
        response = client.fine_tuning.create(
            **training_args,
            verbose=True,
        )

        report_string = f"Successfully submitted a fine-tuning job {response.id}"
        # created_at reports UTC time, we use .astimezone() to convert to local time
        formatted_time = response.created_at.astimezone().strftime("%m/%d/%Y, %H:%M:%S")
        report_string += f" at {formatted_time}"
        rprint(report_string)
    else:
        click.echo("No confirmation received, stopping job launch")
