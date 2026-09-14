from __future__ import annotations

from typing import Any, Literal, Optional, Annotated
from pathlib import Path

from cyclopts import Group, Parameter, validators

from together import BaseModel
from together.types import fine_tuning_estimate_price_params as pe_params
from together.lib.utils import log_warn
from together.lib.cli.api._utils import (
    BoolOrAuto,
    int_or_max_converter,
)
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._prompt import confirm as prompt_confirm
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.resources.fine_tuning import validate_early_stopping
from together.lib.cli.components.model_dump import print_model_dump
from together.lib.cli.components.upload_progress import upload_file_with_progress


def get_confirmation_message(price_line: str, warning: str) -> str:
    return f"""You are about to create a fine-tuning job.
{price_line}

The actual cost of your job will be determined by the model size, the number of tokens in the training file, the number of tokens in the validation file, the number of epochs, and the number of evaluations. Visit https://www.together.ai/pricing to learn more about pricing.
{warning}"""


_WARNING_MESSAGE_INSUFFICIENT_FUNDS = (
    "\n[yellow][bold]The estimated price of this job is significantly greater than your current credit limit and balance combined.[/bold][/yellow] "
    "It will likely get cancelled due to insufficient funds. "
    "Consider increasing your credit limit at https://api.together.ai/settings/profile\n"
)

_PRICE_ESTIMATION_UNAVAILABLE_LINES_BY_REASON = {
    "multimodal_dataset": "[yellow][bold]Price estimation is currently not available for multimodal datasets.[/bold][/yellow]",
    "train_file_not_validated": "[yellow][bold]Price estimation is not available because the training file has not been validated yet.[/bold][/yellow]",
    "eval_file_not_validated": "[yellow][bold]Price estimation is not available because the evaluation file has not been validated yet.[/bold][/yellow]",
    "train_file_invalid": "[yellow][bold]Price estimation is not available because the training file is invalid. If you proceed, your job will be cancelled.[/bold][/yellow]",
    "eval_file_invalid": "[yellow][bold]Price estimation is not available because the evaluation file is invalid. If you proceed, your job will be cancelled.[/bold][/yellow]",
}
_PRICE_ESTIMATION_UNAVAILABLE_LINE_DEFAULT = "Price estimation is not available for this job."

# Maps each file-specific unavailable reason to the training_args key holding the relevant file ID,
# so the hint can point the user at the exact file to inspect.
_PRICE_ESTIMATION_UNAVAILABLE_FILE_ARG_BY_REASON = {
    "train_file_not_validated": "training_file",
    "eval_file_not_validated": "validation_file",
    "train_file_invalid": "training_file",
    "eval_file_invalid": "validation_file",
}
_FILE_DETAILS_HINT = (
    "Run [bold]tg files retrieve {file_id} --json[/bold] to get details about the file processing status."
)


def _check_path_exists(path_string: Optional[str]) -> bool:
    if path_string == "" or path_string is None:
        return False
    p = Path(path_string)
    if p.is_dir():
        raise ValueError(f"Path {path_string} is a directory, not a file. Please provide a file path.")
    return p.exists() and p.is_file()


model_group = Group(
    "Model",
    help="You must specify either a model or a checkpoint to start a job from, not both",
    default_parameter=Parameter(negative=""),  # Disable "--no-" flags
    validator=validators.LimitedChoice(),  # Mutually Exclusive Options
    sort_key=0,
)

DEFAULT_LEARNING_RATE = 1e-5
DEFAULT_LORA_R = 8
DEFAULT_LORA_ALPHA = 8


async def create(
    training_file: Annotated[
        str,
        Parameter(
            alias="-t",
            help="Training file ID from Files API or local path to a file to upload",
        ),
    ],
    validation_file: Annotated[
        Optional[str],
        Parameter(
            alias="-v",
            help="Validation file ID from Files API or local path to a file to upload",
        ),
    ] = None,
    model: Annotated[
        Optional[str], Parameter(group=model_group, alias="-M", help="Name of the base model to run fine-tune job on")
    ] = None,
    from_checkpoint: Annotated[
        Optional[str],
        Parameter(
            group=model_group,
            help="Checkpoint to continue training from a previous fine-tuning job, formatted as `JOB_ID/OUTPUT_MODEL_NAME:STEP`; STEP is optional and defaults to the final checkpoint",
        ),
    ] = None,
    n_epochs: Annotated[int, Parameter(alias="--ne", help="Number of epochs to train for")] = 1,
    packing: Annotated[bool, Parameter(show_default=True, help="Whether to use packing for training")] = True,
    n_evals: Annotated[int, Parameter(help="Number of evaluation loops to run")] = 0,
    max_seq_length: Annotated[int | None, Parameter(help="Maximum sequence length to use for training")] = None,
    n_checkpoints: Annotated[int, Parameter(alias="-c", help="Number of checkpoints to save")] = 1,
    batch_size: Annotated[
        int | Literal["max"],
        Parameter(converter=int_or_max_converter, alias="-b", help="Train batch size"),
    ] = "max",
    gradient_accumulation_steps: Annotated[
        Optional[int],
        Parameter(help="Number of gradient accumulation steps (increases effective batch size without more memory)"),
    ] = None,
    learning_rate: Annotated[float, Parameter(alias="--lr", help="Learning rate")] = DEFAULT_LEARNING_RATE,
    lr_scheduler_type: Annotated[
        Literal["linear", "cosine"], Parameter(help="Learning rate scheduler type")
    ] = "cosine",
    min_lr_ratio: Annotated[
        float, Parameter(help="Min learning rate ratio of the initial learning rate for the learning rate scheduler")
    ] = 0.0,
    scheduler_num_cycles: Annotated[
        float, Parameter(help="Number or fraction of cycles for the cosine learning rate scheduler")
    ] = 0.5,
    warmup_ratio: Annotated[float, Parameter(help="Warmup ratio for the learning rate scheduler")] = 0.0,
    max_grad_norm: Annotated[float, Parameter(help="Max gradient norm for clipping (0 to disable)")] = 1.0,
    weight_decay: Annotated[float, Parameter(help="Weight decay")] = 0.0,
    lora: Annotated[Optional[bool], Parameter(help="Whether to use LoRA adapters for fine-tuning")] = None,
    lora_r: Annotated[int, Parameter(help="Rank of the LoRA adapter matrices")] = DEFAULT_LORA_R,
    lora_dropout: Annotated[float, Parameter(help="Dropout probability applied to LoRA adapter inputs")] = 0,
    lora_alpha: Annotated[
        float, Parameter(help="Scaling factor applied to the LoRA adapter weights")
    ] = DEFAULT_LORA_ALPHA,
    lora_trainable_modules: Annotated[
        str,
        Parameter(
            help=(
                "LoRA target modules (e.g. 'all-linear', 'q_proj,v_proj'). "
                "Fine-tunes targeting MoE expert modules (w_up, w_gate, w_down) produce adapter-only output."
            )
        ),
    ] = "all-linear",
    training_method: Annotated[
        Literal["sft", "dpo"],
        Parameter(
            alias=("-m"),
            help="Training method to use: sft (supervised fine-tuning) or dpo (Direct Preference Optimization)",
        ),
    ] = "sft",
    dpo_beta: Annotated[Optional[float], Parameter(help="DPO beta parameter")] = None,
    dpo_normalize_logratios_by_length: Annotated[
        bool, Parameter(help="Whether to normalize logratios by sample length")
    ] = False,
    rpo_alpha: Annotated[Optional[float], Parameter(help="RPO alpha parameter")] = None,
    simpo_gamma: Annotated[Optional[float], Parameter(help="SimPO gamma parameter")] = None,
    suffix: Annotated[Optional[str], Parameter(help="Suffix for the fine-tuned model name")] = None,
    wandb_api_key: Annotated[Optional[str], Parameter(help="Wandb API key")] = None,
    wandb_base_url: Annotated[Optional[str], Parameter(help="Wandb base URL")] = None,
    wandb_project_name: Annotated[Optional[str], Parameter(help="Wandb project name")] = None,
    wandb_name: Annotated[Optional[str], Parameter(help="Wandb run name")] = None,
    wandb_entity: Annotated[Optional[str], Parameter(help="Wandb entity name")] = None,
    random_seed: Annotated[
        Optional[int],
        Parameter(help="Random seed for reproducible training, e.g. 42; uses the server default if unset"),
    ] = None,
    early_stopping_enabled: Annotated[
        bool,
        Parameter(
            help="Stop training early when validation eval_loss stops improving (requires --validation-file and --n-evals)",
            negative=(),
        ),
    ] = False,
    early_stopping_patience: Annotated[
        Optional[int],
        Parameter(help="Consecutive non-improving evals to tolerate before stopping; uses the default (2) if unset"),
    ] = None,
    early_stopping_min_delta: Annotated[
        Optional[float],
        Parameter(help="Minimum eval_loss decrease to count as an improvement; uses the default (0) if unset"),
    ] = None,
    early_stopping_warmup_evals: Annotated[
        Optional[int],
        Parameter(help="Initial evals to skip before counting patience; uses the default (1) if unset"),
    ] = None,
    confirm: Annotated[
        bool, Parameter(alias=("-y"), negative=(), help="Whether to skip the launch confirmation message")
    ] = False,
    train_on_inputs: Annotated[
        Optional[BoolOrAuto],
        Parameter(
            help="Whether to mask user messages (conversational) or prompts (instruction); 'auto' detects from data format",
        ),
    ] = None,
    train_vision: Annotated[bool, Parameter(help="Train the vision encoder (multimodal models only)")] = False,
    from_hf_model: Annotated[
        Optional[str],
        Parameter(
            help="Hugging Face Hub repo to start training from; should match the base model's architecture and size",
        ),
    ] = None,
    hf_model_revision: Annotated[
        Optional[str],
        Parameter(
            help="Revision of the Hugging Face Hub model, either a branch name (e.g. `main` for the latest revision) or a specific commit hash",
        ),
    ] = None,
    hf_api_token: Annotated[
        Optional[str], Parameter(help="HF API token to use for uploading a checkpoint to a private repo")
    ] = None,
    hf_output_repo_name: Annotated[Optional[str], Parameter(help="HF repo to upload the fine-tuned model to")] = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """Start fine-tuning."""
    training_args: dict[str, Any] = dict(
        training_file=training_file,
        model=model,
        n_epochs=n_epochs,
        validation_file=validation_file,
        packing=packing,
        n_evals=n_evals,
        max_seq_length=max_seq_length,
        n_checkpoints=n_checkpoints,
        batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
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
        wandb_entity=wandb_entity,
        random_seed=random_seed,
        train_on_inputs=train_on_inputs.value if train_on_inputs is not None else None,
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
        raise ValueError("Either --model or --from-checkpoint is required")

    model_name = model
    if from_checkpoint is not None:
        model_name = from_checkpoint.split(":")[0]
    model_limits = await config.client.fine_tuning.model_limits(model_name=str(model_name))

    if lora is None:
        pass
    elif lora:
        # Cyclopts has no Click-style ctx/ParameterSource; use CLI defaults as heuristic for "unset".
        if lora_r == DEFAULT_LORA_R:
            training_args["lora_r"] = model_limits.lora_training.max_rank
        if learning_rate == DEFAULT_LEARNING_RATE:
            training_args["learning_rate"] = 1e-3
        if lora_alpha == DEFAULT_LORA_ALPHA:
            training_args["lora_alpha"] = training_args["lora_r"] * 2
    else:
        if model_limits.full_training is None:
            raise ValueError(f"Full fine-tuning is not supported for the model `{model}`")
        if any([lora_r != 8, lora_dropout != 0, lora_alpha != 8, lora_trainable_modules != "all-linear"]):
            raise ValueError(
                "You set LoRA parameters for a full fine-tuning job. Please use --lora or remove LoRA parameters."
            )

    if n_evals <= 0 and validation_file:
        log_warn(
            "Warning: You have specified a validation file but the number of evaluation loops is set to 0. "
            "No evaluations will be performed."
        )
    elif n_evals > 0 and not validation_file:
        raise ValueError("You have specified a number of evaluation loops but no validation file.")

    validate_early_stopping(
        early_stopping_enabled=early_stopping_enabled,
        early_stopping_patience=early_stopping_patience,
        early_stopping_min_delta=early_stopping_min_delta,
        early_stopping_warmup_evals=early_stopping_warmup_evals,
        n_evals=n_evals,
        validation_file=validation_file,
    )

    if early_stopping_enabled:
        training_args["early_stopping_enabled"] = early_stopping_enabled
        training_args["early_stopping_patience"] = early_stopping_patience
        training_args["early_stopping_min_delta"] = early_stopping_min_delta
        training_args["early_stopping_warmup_evals"] = early_stopping_warmup_evals

    training_type_cls: pe_params.TrainingType | None
    if lora is None:
        # User did not provide --lora/--no-lora, so the training type will be determined automatically.
        # By default, the API uses LoRA, or inherits the training type from the parent job
        # when --from-checkpoint is specified.
        # This logic is handled on the Together API backend.
        training_type_cls = None
    elif lora:
        training_type_cls = pe_params.TrainingTypeLoRaTrainingType(
            lora_alpha=int(training_args["lora_alpha"]),
            lora_r=training_args["lora_r"],
            lora_dropout=training_args["lora_dropout"],
            lora_trainable_modules=training_args["lora_trainable_modules"],
            type="Lora",
        )
    else:
        training_type_cls = pe_params.TrainingTypeFullTrainingType(type="Full")

    training_method_cls: pe_params.TrainingMethod
    if training_method == "sft":
        train_on_inputs_val = train_on_inputs or BoolOrAuto("auto")
        training_args["train_on_inputs"] = train_on_inputs_val.value
        training_method_cls = pe_params.TrainingMethodTrainingMethodSft(
            method="sft",
            train_on_inputs=train_on_inputs_val.value,
        )
    else:
        training_method_cls = pe_params.TrainingMethodTrainingMethodDpo(
            method="dpo",
            dpo_beta=dpo_beta or 0,
            dpo_normalize_logratios_by_length=dpo_normalize_logratios_by_length,
            dpo_reference_free=False,
            rpo_alpha=rpo_alpha or 0,
            simpo_gamma=simpo_gamma or 0,
        )

    if max_seq_length is not None:
        if max_seq_length < model_limits.min_max_seq_length:
            raise ValueError(f"Maximum sequence length must be greater than {model_limits.min_max_seq_length}")
        if training_method == "sft" and max_seq_length > model_limits.max_seq_length_sft:
            raise ValueError(
                f"Maximum sequence length for SFT training must be less than {model_limits.max_seq_length_sft}"
            )
        elif training_method == "dpo" and max_seq_length > model_limits.max_seq_length_dpo:
            raise ValueError(
                f"Maximum sequence length for DPO training must be less than {model_limits.max_seq_length_dpo}"
            )
        training_args["max_seq_length"] = max_seq_length

    # If the user passes a path to a file, try to upload it to the files API first
    # Uploads are idempotent so we can depend on this API always giving us a file ID
    if _check_path_exists(training_args["training_file"]):
        training_path = Path(training_args["training_file"])
        file_upload = await upload_file_with_progress(
            config.client.files.upload,
            training_path,
            enabled=not config.json,
            description=f"Uploading training file {training_path.name}",
            purpose="fine-tune",
        )
        training_args["training_file"] = file_upload.id

    # If the user passes a path to a file, try to upload it to the files API first
    # Uploads are idempotent so we can depend on this API always giving us a file ID
    if _check_path_exists(training_args["validation_file"]):
        validation_path = Path(training_args["validation_file"])
        file_upload = await upload_file_with_progress(
            config.client.files.upload,
            validation_path,
            enabled=not config.json,
            description=f"Uploading validation file {validation_path.name}",
            purpose="fine-tune",
        )
        training_args["validation_file"] = file_upload.id

    finetune_price_estimation_result = await show_loading_status(
        "Estimating fine-tuning price...",
        config.client.fine_tuning.estimate_price(
            training_file=training_args["training_file"],
            validation_file=training_args["validation_file"],
            model=model or "",
            from_checkpoint=from_checkpoint or "",
            n_epochs=n_epochs,
            n_evals=n_evals,
            training_type=training_type_cls,
            training_method=training_method_cls,
        ),
    )
    estimated_price = (
        finetune_price_estimation_result.estimated_total_price
        if finetune_price_estimation_result.estimation_available is not False
        else None
    )
    if finetune_price_estimation_result.estimation_available is False or estimated_price is None:
        if finetune_price_estimation_result.estimation_available is False:
            unavailable_reason = finetune_price_estimation_result.unavailable_reason
            price_line = _PRICE_ESTIMATION_UNAVAILABLE_LINES_BY_REASON.get(
                unavailable_reason,
                _PRICE_ESTIMATION_UNAVAILABLE_LINE_DEFAULT,
            )
            file_arg = _PRICE_ESTIMATION_UNAVAILABLE_FILE_ARG_BY_REASON.get(unavailable_reason)
        else:
            price_line = _PRICE_ESTIMATION_UNAVAILABLE_LINE_DEFAULT
            file_arg = None
        file_id = training_args.get(file_arg) if file_arg else None
        if file_id:
            price_line += " " + _FILE_DETAILS_HINT.format(file_id=file_id)
        warning = ""
    else:
        price_str = f"${estimated_price:.2f}"
        price_line = f"The estimated price of this job is [bold]{price_str}[/bold]."
        warning = _WARNING_MESSAGE_INSUFFICIENT_FUNDS if not finetune_price_estimation_result.allowed_to_proceed else ""

    if not confirm:
        console.print(get_confirmation_message(price_line=price_line, warning=warning))
        if not config.non_interactive and not await prompt_confirm("Do you want to proceed?"):
            return

    console.print(f"Submitting a fine-tuning job with the following parameters:")
    print_model_dump(BaseModel(**training_args), show_nulls=False, expand=False, padding=(0, 2))

    response = await show_loading_status(
        "Creating fine-tuning job...", config.client.fine_tuning.create(**training_args)
    )
    url = f"https://api.together.ai/fine-tuning/{response.id}"
    console.print(
        f"\n[green]√ Fine-tuning job has been submitted.[/green] [dim]([link={url}]{response.id}[/link])[/dim]"
    )
    console.print(f"\n  You can track the job's progress with the following command:")
    console.print(f"  [dim]-[/dim] [primary]tg fine-tuning {response.id}[/primary]")
