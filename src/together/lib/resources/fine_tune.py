from __future__ import annotations

from typing import Literal

from ..utils import log_warn_once
from ..types.fine_tune import (
    FinetuneTrainingLimits,
)
from ...types.fine_tune_create_params import (
    LrScheduler,
    TrainingType,
    TrainingMethod,
    FineTuneCreateParams,
    TrainingTypeFullTrainingType,
    TrainingTypeLoRaTrainingType,
    TrainingMethodTrainingMethodDpo,
    TrainingMethodTrainingMethodSft,
    LrSchedulerLrSchedulerArgsCosineLrSchedulerArgs,
    LrSchedulerLrSchedulerArgsLinearLrSchedulerArgs,
)

AVAILABLE_TRAINING_METHODS = {
    "sft",
    "dpo",
}


def create_finetune_request(
    model_limits: FinetuneTrainingLimits,
    training_file: str,
    model: str | None = None,
    n_epochs: int = 1,
    validation_file: str | None = "",
    n_evals: int | None = 0,
    n_checkpoints: int | None = 1,
    batch_size: int | Literal["max"] = "max",
    learning_rate: float | None = 0.00001,
    lr_scheduler_type: Literal["linear", "cosine"] = "linear",
    min_lr_ratio: float | None = 0.0,
    scheduler_num_cycles: float = 0.5,
    warmup_ratio: float | None = None,
    max_grad_norm: float = 1.0,
    weight_decay: float | None = 0.0,
    lora: bool = False,
    lora_r: int | None = None,
    lora_dropout: float | None = 0,
    lora_alpha: int | None = None,
    lora_trainable_modules: str | None = "all-linear",
    suffix: str | None = None,
    wandb_api_key: str | None = None,
    wandb_base_url: str | None = None,
    wandb_project_name: str | None = None,
    wandb_name: str | None = None,
    train_on_inputs: bool | Literal["auto"] | None = None,
    training_method: str = "sft",
    dpo_beta: float | None = None,
    from_checkpoint: str | None = None,
) -> FineTuneCreateParams:
    if model is not None and from_checkpoint is not None:
        raise ValueError("You must specify either a model or a checkpoint to start a job from, not both")

    if model is None and from_checkpoint is None:
        raise ValueError("You must specify either a model or a checkpoint")

    model_or_checkpoint = model or from_checkpoint

    if batch_size == "max":
        log_warn_once(
            "Starting from together>=1.3.0, the default batch size is set to the maximum allowed value for each model."
        )
    if warmup_ratio is None:
        warmup_ratio = 0.0

    training_type: TrainingType = TrainingTypeFullTrainingType(type="Full")
    max_batch_size: int = 0
    max_batch_size_dpo: int = 0
    min_batch_size: int = 0
    if lora:
        if model_limits.lora_training is None:
            raise ValueError(f"LoRA adapters are not supported for the selected model ({model_or_checkpoint}).")
        lora_r = lora_r if lora_r is not None else model_limits.lora_training.max_rank
        lora_alpha = lora_alpha if lora_alpha is not None else lora_r * 2
        training_type = TrainingTypeLoRaTrainingType(
            type="Lora",
            lora_r=lora_r,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,  # type: ignore
            lora_trainable_modules=lora_trainable_modules,  # type: ignore
        )

        max_batch_size = model_limits.lora_training.max_batch_size
        min_batch_size = model_limits.lora_training.min_batch_size
        max_batch_size_dpo = model_limits.lora_training.max_batch_size_dpo
    else:
        if model_limits.full_training is None:
            raise ValueError(f"Full training is not supported for the selected model ({model_or_checkpoint}).")

        max_batch_size = model_limits.full_training.max_batch_size
        min_batch_size = model_limits.full_training.min_batch_size
        max_batch_size_dpo = model_limits.full_training.max_batch_size_dpo

    if batch_size == "max":
        if training_method == "dpo":
            batch_size = max_batch_size_dpo
        else:
            batch_size = max_batch_size

    if training_method == "sft":
        if batch_size > max_batch_size:
            raise ValueError(
                f"Requested batch size of {batch_size} is higher that the maximum allowed value of {max_batch_size}."
            )
    elif training_method == "dpo":
        if batch_size > max_batch_size_dpo:
            raise ValueError(
                f"Requested batch size of {batch_size} is higher that the maximum allowed value of {max_batch_size_dpo}."
            )

    if batch_size < min_batch_size:
        raise ValueError(
            f"Requested batch size of {batch_size} is lower that the minimum allowed value of {min_batch_size}."
        )

    if warmup_ratio > 1 or warmup_ratio < 0:
        raise ValueError(f"Warmup ratio should be between 0 and 1 (got {warmup_ratio})")

    if min_lr_ratio is not None and (min_lr_ratio > 1 or min_lr_ratio < 0):
        raise ValueError(f"Min learning rate ratio should be between 0 and 1 (got {min_lr_ratio})")

    if max_grad_norm < 0:
        raise ValueError(f"Max gradient norm should be non-negative (got {max_grad_norm})")

    if weight_decay is not None and (weight_decay < 0):
        raise ValueError(f"Weight decay should be non-negative (got {weight_decay})")

    if training_method not in AVAILABLE_TRAINING_METHODS:
        raise ValueError(f"training_method must be one of {', '.join(AVAILABLE_TRAINING_METHODS)}")

    if train_on_inputs is not None and training_method != "sft":
        raise ValueError("train_on_inputs is only supported for SFT training")

    if train_on_inputs is None and training_method == "sft":
        log_warn_once("train_on_inputs is not set for SFT training, it will be set to 'auto'")
        train_on_inputs = "auto"

    if dpo_beta is not None and training_method != "dpo":
        raise ValueError("dpo_beta is only supported for DPO training")

    lr_scheduler: LrScheduler
    if lr_scheduler_type == "cosine":
        if scheduler_num_cycles <= 0.0:
            raise ValueError(f"Number of cycles should be greater than 0 (got {scheduler_num_cycles})")

        lr_scheduler = LrScheduler(
            lr_scheduler_type="cosine",
            lr_scheduler_args=LrSchedulerLrSchedulerArgsCosineLrSchedulerArgs(
                min_lr_ratio=min_lr_ratio,  # type: ignore
                num_cycles=scheduler_num_cycles,
            ),
        )
    else:
        lr_scheduler = LrScheduler(
            lr_scheduler_type="linear",
            lr_scheduler_args=LrSchedulerLrSchedulerArgsLinearLrSchedulerArgs(min_lr_ratio=min_lr_ratio),  # type: ignore
        )

    training_method_cls: TrainingMethod
    if training_method == "sft":
        training_method_cls = TrainingMethodTrainingMethodSft(method="sft", train_on_inputs=train_on_inputs)  # type: ignore
    elif training_method == "dpo":
        training_method_cls = TrainingMethodTrainingMethodDpo(method="dpo", dpo_beta=dpo_beta)  # type: ignore

    finetune_request = FineTuneCreateParams(
        model=model,  # type: ignore
        training_file=training_file,
        validation_file=validation_file,  # type: ignore
        n_epochs=n_epochs,
        n_evals=n_evals,  # type: ignore
        n_checkpoints=n_checkpoints,  # type: ignore
        batch_size=batch_size,
        learning_rate=learning_rate,  # type: ignore
        lr_scheduler=lr_scheduler,
        warmup_ratio=warmup_ratio,
        max_grad_norm=max_grad_norm,
        weight_decay=weight_decay,  # type: ignore
        training_type=training_type,
        suffix=suffix,  # type: ignore
        wandb_key=wandb_api_key,
        wandb_base_url=wandb_base_url,  # type: ignore
        wandb_project_name=wandb_project_name,  # type: ignore
        wandb_name=wandb_name,  # type: ignore
        training_method=training_method_cls,  # type: ignore
        from_checkpoint=from_checkpoint,  # type: ignore
    )

    return finetune_request
