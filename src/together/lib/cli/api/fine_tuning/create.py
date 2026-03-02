from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any, Literal, Optional

from cyclopts import Parameter

from together import AsyncTogether
from together.types import fine_tuning_estimate_price_params as pe_params
from together.lib.resources.fine_tuning import async_get_model_limits
from together.lib.utils import log_warn
from together.lib.cli.api._utils import (
    int_or_max_converter,
    bool_or_auto_converter,
)


def get_confirmation_message(price: str, warning: str) -> str:
    return (
        "\nYou are about to create a fine-tuning job. The estimated price of this job is "
        f"{price}\n\n"
        "The actual cost of your job will be determined by the model size, the number of tokens "
        "in the training file, the number of tokens in the validation file, the number of epochs, and "
        "the number of evaluations. Visit https://www.together.ai/pricing to learn more about pricing.\n"
        f"{warning}\nDo you want to proceed? [Y/n]"
    )


_WARNING_MESSAGE_INSUFFICIENT_FUNDS = (
    "\nThe estimated price of this job is significantly greater than your current credit limit and balance combined. "
    "It will likely get cancelled due to insufficient funds. "
    "Consider increasing your credit limit at https://api.together.xyz/settings/profile\n"
)


def _check_path_exists(path_string: str) -> bool:
    if path_string == "":
        return False
    p = Path(path_string)
    return p.exists() and (p.is_file() or p.is_dir())


async def create(
    training_file: Annotated[str, Parameter(name=["--training-file", "-t"])],
    validation_file: str = "",
    model: Optional[str] = None,
    n_epochs: int = 1,
    n_evals: int = 0,
    n_checkpoints: int = 1,
    batch_size: Annotated[
        int | Literal["max"],
        Parameter(converter=int_or_max_converter, name=["--batch-size", "-b"]),
    ] = "max",
    learning_rate: float = 1e-5,
    lr_scheduler_type: Literal["linear", "cosine"] = "cosine",
    min_lr_ratio: float = 0.0,
    scheduler_num_cycles: float = 0.5,
    warmup_ratio: float = 0.0,
    max_grad_norm: float = 1.0,
    weight_decay: float = 0.0,
    lora: bool = True,
    lora_r: int = 8,
    lora_dropout: float = 0,
    lora_alpha: float = 8,
    lora_trainable_modules: str = "all-linear",
    training_method: Literal["sft", "dpo"] = "sft",
    dpo_beta: Optional[float] = None,
    dpo_normalize_logratios_by_length: bool = False,
    rpo_alpha: Optional[float] = None,
    simpo_gamma: Optional[float] = None,
    suffix: Optional[str] = None,
    wandb_api_key: Optional[str] = None,
    wandb_base_url: Optional[str] = None,
    wandb_project_name: Optional[str] = None,
    wandb_name: Optional[str] = None,
    confirm: bool = False,
    train_on_inputs: Annotated[
        Optional[tuple[bool | None, Literal["auto"] | None]],
        Parameter(converter=bool_or_auto_converter),
    ] = (None, None),
    train_vision: bool = False,
    from_checkpoint: Optional[str] = None,
    from_hf_model: Optional[str] = None,
    hf_model_revision: Optional[str] = None,
    hf_api_token: Optional[str] = None,
    hf_output_repo_name: Optional[str] = None,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Start fine-tuning."""
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
        raise ValueError("Either --model or --from-checkpoint is required")

    model_name = model
    if from_checkpoint is not None:
        model_name = from_checkpoint.split(":")[0]
    model_limits = await async_get_model_limits(client, str(model_name))

    if lora:
        if model_limits.lora_training is None:
            raise ValueError(f"LoRA fine-tuning is not supported for the model `{model}`")
        training_args["lora_r"] = model_limits.lora_training.max_rank
        training_args["learning_rate"] = 1e-3
        training_args["lora_alpha"] = training_args["lora_r"] * 2
    else:
        if model_limits.full_training is None:
            raise ValueError(f"Full fine-tuning is not supported for the model `{model}`")
        if any([lora_r != 8, lora_dropout != 0, lora_alpha != 8, lora_trainable_modules != "all-linear"]):
            raise ValueError(
                "You set LoRA parameters for a full fine-tuning job. "
                "Please use --lora or remove LoRA parameters."
            )

    if n_evals <= 0 and validation_file:
        log_warn(
            "Warning: You have specified a validation file but the number of evaluation loops is set to 0. "
            "No evaluations will be performed."
        )
    elif n_evals > 0 and not validation_file:
        raise ValueError("You have specified a number of evaluation loops but no validation file.")

    if lora:
        training_type_cls = pe_params.TrainingTypeLoRaTrainingType(
            lora_alpha=int(training_args["lora_alpha"]),
            lora_r=training_args["lora_r"],
            lora_dropout=training_args["lora_dropout"],
            lora_trainable_modules=training_args["lora_trainable_modules"],
            type="Lora",
        )
    else:
        training_type_cls = pe_params.TrainingTypeFullTrainingType(type="Full")

    if training_method == "sft":
        train_on_inputs_val = train_on_inputs or "auto"
        training_args["train_on_inputs"] = train_on_inputs_val
        training_method_cls = pe_params.TrainingMethodTrainingMethodSft(
            method="sft",
            train_on_inputs=train_on_inputs_val,
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

    if model_limits.supports_vision:
        confirm = True

    if _check_path_exists(training_args["training_file"]):
        file_upload = await client.files.upload(Path(training_args["training_file"]), purpose="fine-tune")
        training_args["training_file"] = file_upload.id
    if _check_path_exists(training_args["validation_file"]):
        file_upload = await client.files.upload(Path(training_args["validation_file"]), purpose="fine-tune")
        training_args["validation_file"] = file_upload.id

    finetune_price_estimation_result = await client.fine_tuning.estimate_price(
        training_file=training_args["training_file"],
        validation_file=training_args["validation_file"],
        model=model or "",
        from_checkpoint=from_checkpoint or "",
        n_epochs=n_epochs,
        n_evals=n_evals,
        training_type=training_type_cls,
        training_method=training_method_cls,
    )
    price_str = f"${finetune_price_estimation_result.estimated_total_price:.2f}"
    warning = _WARNING_MESSAGE_INSUFFICIENT_FUNDS if not finetune_price_estimation_result.allowed_to_proceed else ""
    confirmation_message = get_confirmation_message(price=price_str, warning=warning)

    if not confirm:
        resp = input(confirmation_message).strip().lower()
        if resp and resp != "y" and resp != "yes":
            return
    response = await client.fine_tuning.create(**training_args, verbose=True)
    print(f"\n\nSuccess! Your fine-tuning job {response.id} has been submitted.")
