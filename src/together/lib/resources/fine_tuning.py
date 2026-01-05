from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from rich import print as rprint

from together.types import fine_tuning_estimate_price_params as pe_params
from together.lib.utils import log_warn_once

if TYPE_CHECKING:
    from together import Together, AsyncTogether
from together.lib.types.fine_tuning import (
    TrainingType,
    FinetuneRequest,
    FullTrainingType,
    LoRATrainingType,
    CosineLRScheduler,
    LinearLRScheduler,
    TrainingMethodDPO,
    TrainingMethodSFT,
    FinetuneLRScheduler,
    CosineLRSchedulerArgs,
    LinearLRSchedulerArgs,
    FinetuneTrainingLimits,
    FinetuneMultimodalParams,
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
    lr_scheduler_type: Literal["linear", "cosine"] = "cosine",
    min_lr_ratio: float | None = 0.0,
    scheduler_num_cycles: float = 0.5,
    warmup_ratio: float | None = None,
    max_grad_norm: float = 1.0,
    weight_decay: float | None = 0.0,
    lora: bool = False,
    lora_r: int | None = None,
    lora_dropout: float | None = 0,
    lora_alpha: float | None = None,
    lora_trainable_modules: str | None = "all-linear",
    train_vision: bool = False,
    suffix: str | None = None,
    wandb_api_key: str | None = None,
    wandb_base_url: str | None = None,
    wandb_project_name: str | None = None,
    wandb_name: str | None = None,
    train_on_inputs: bool | Literal["auto"] | None = None,
    training_method: str = "sft",
    dpo_beta: float | None = None,
    dpo_normalize_logratios_by_length: bool = False,
    rpo_alpha: float | None = None,
    simpo_gamma: float | None = None,
    from_checkpoint: str | None = None,
    from_hf_model: str | None = None,
    hf_model_revision: str | None = None,
    hf_api_token: str | None = None,
    hf_output_repo_name: str | None = None,
) -> tuple[FinetuneRequest, pe_params.TrainingType, pe_params.TrainingMethod]:
    if model is not None and from_checkpoint is not None:
        raise ValueError("You must specify either a model or a checkpoint to start a job from, not both")

    if model is None and from_checkpoint is None:
        raise ValueError("You must specify either a model or a checkpoint")

    if from_checkpoint is not None and from_hf_model is not None:
        raise ValueError(
            "You must specify either a Hugging Face Hub model or a previous checkpoint from "
            "Together to start a job from, not both"
        )

    if from_hf_model is not None and model is None:
        raise ValueError("You must specify the base model to fine-tune a model from the Hugging Face Hub")

    model_or_checkpoint = model or from_checkpoint

    if warmup_ratio is None:
        warmup_ratio = 0.0

    training_type: TrainingType = FullTrainingType()
    if lora:
        if model_limits.lora_training is None:
            raise ValueError(f"LoRA adapters are not supported for the selected model ({model_or_checkpoint}).")

        if lora_dropout is not None:
            if not 0 <= lora_dropout < 1.0:
                raise ValueError("LoRA dropout must be in [0, 1) range.")

        lora_r = lora_r if lora_r is not None else model_limits.lora_training.max_rank
        lora_alpha = lora_alpha if lora_alpha is not None else lora_r * 2
        training_type = LoRATrainingType(
            lora_r=lora_r,
            lora_alpha=int(lora_alpha),
            lora_dropout=lora_dropout or 0.0,
            lora_trainable_modules=lora_trainable_modules or "all-linear",
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

    if batch_size != "max":
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

    if dpo_beta is not None and training_method != "dpo":
        raise ValueError("dpo_beta is only supported for DPO training")
    if dpo_normalize_logratios_by_length and training_method != "dpo":
        raise ValueError("dpo_normalize_logratios_by_length=True is only supported for DPO training")
    if rpo_alpha is not None:
        if training_method != "dpo":
            raise ValueError("rpo_alpha is only supported for DPO training")
        if not rpo_alpha >= 0.0:
            raise ValueError(f"rpo_alpha should be non-negative (got {rpo_alpha})")

    if simpo_gamma is not None:
        if training_method != "dpo":
            raise ValueError("simpo_gamma is only supported for DPO training")
        if not simpo_gamma >= 0.0:
            raise ValueError(f"simpo_gamma should be non-negative (got {simpo_gamma})")

    lr_scheduler: FinetuneLRScheduler
    if lr_scheduler_type == "cosine":
        if scheduler_num_cycles <= 0.0:
            raise ValueError(f"Number of cycles should be greater than 0 (got {scheduler_num_cycles})")

        lr_scheduler = CosineLRScheduler(
            lr_scheduler_args=CosineLRSchedulerArgs(min_lr_ratio=min_lr_ratio, num_cycles=scheduler_num_cycles),
        )
    else:
        lr_scheduler = LinearLRScheduler(
            lr_scheduler_args=LinearLRSchedulerArgs(min_lr_ratio=min_lr_ratio),
        )

    training_method_cls: TrainingMethodSFT | TrainingMethodDPO
    if training_method == "sft":
        if train_on_inputs is None:
            log_warn_once("train_on_inputs is not set for SFT training, it will be set to 'auto'")
            train_on_inputs = "auto"
        training_method_cls = TrainingMethodSFT(train_on_inputs=train_on_inputs)
    elif training_method == "dpo":
        if simpo_gamma is not None and simpo_gamma > 0:
            dpo_reference_free = True
            dpo_normalize_logratios_by_length = True
            rprint(
                f"Parameter simpo_gamma was set to {simpo_gamma}. "
                "SimPO training detected. Reference logits will not be used "
                "and length normalization of log-probabilities will be enabled."
            )
        else:
            dpo_reference_free = False

        training_method_cls = TrainingMethodDPO(
            dpo_beta=dpo_beta,
            dpo_normalize_logratios_by_length=dpo_normalize_logratios_by_length,
            dpo_reference_free=dpo_reference_free,
            rpo_alpha=rpo_alpha,
            simpo_gamma=simpo_gamma,
        )

    if model_limits.supports_vision:
        multimodal_params = FinetuneMultimodalParams(train_vision=train_vision)
    elif not model_limits.supports_vision and train_vision:
        raise ValueError(f"Vision encoder training is not supported for the non-multimodal model `{model}`")
    else:
        multimodal_params = None

    finetune_request = FinetuneRequest(
        model=model,
        training_file=training_file,
        validation_file=validation_file,
        n_epochs=n_epochs,
        n_evals=n_evals,
        n_checkpoints=n_checkpoints,
        batch_size=batch_size,
        learning_rate=learning_rate or 0.00001,
        lr_scheduler=lr_scheduler,
        warmup_ratio=warmup_ratio,
        max_grad_norm=max_grad_norm,
        weight_decay=weight_decay or 0.0,
        training_type=training_type,
        suffix=suffix,
        wandb_key=wandb_api_key,
        wandb_base_url=wandb_base_url,
        wandb_project_name=wandb_project_name,
        wandb_name=wandb_name,
        training_method=training_method_cls,  # pyright: ignore[reportPossiblyUnboundVariable]
        multimodal_params=multimodal_params,
        from_checkpoint=from_checkpoint,
        from_hf_model=from_hf_model,
        hf_model_revision=hf_model_revision,
        hf_api_token=hf_api_token,
        hf_output_repo_name=hf_output_repo_name,
    )

    training_type_pe, training_method_pe = create_price_estimation_params(finetune_request)

    return finetune_request, training_type_pe, training_method_pe


def create_price_estimation_params(
    finetune_request: FinetuneRequest,
) -> tuple[pe_params.TrainingType, pe_params.TrainingMethod]:
    training_type_cls: pe_params.TrainingType
    if isinstance(finetune_request.training_type, FullTrainingType):
        training_type_cls = pe_params.TrainingTypeFullTrainingType(
            type="Full",
        )
    elif isinstance(finetune_request.training_type, LoRATrainingType):
        training_type_cls = pe_params.TrainingTypeLoRaTrainingType(
            lora_alpha=finetune_request.training_type.lora_alpha,
            lora_r=finetune_request.training_type.lora_r,
            lora_dropout=finetune_request.training_type.lora_dropout,
            lora_trainable_modules=finetune_request.training_type.lora_trainable_modules,
            type="Lora",
        )
    else:
        raise ValueError(f"Unknown training type: {finetune_request.training_type}")

    training_method_cls: pe_params.TrainingMethod
    if isinstance(finetune_request.training_method, TrainingMethodSFT):
        training_method_cls = pe_params.TrainingMethodTrainingMethodSft(
            method="sft",
            train_on_inputs=finetune_request.training_method.train_on_inputs,
        )
    elif isinstance(finetune_request.training_method, TrainingMethodDPO):
        training_method_cls = pe_params.TrainingMethodTrainingMethodDpo(
            method="dpo",
            dpo_beta=finetune_request.training_method.dpo_beta or 0,
            dpo_normalize_logratios_by_length=finetune_request.training_method.dpo_normalize_logratios_by_length,
            dpo_reference_free=finetune_request.training_method.dpo_reference_free,
            rpo_alpha=finetune_request.training_method.rpo_alpha or 0,
            simpo_gamma=finetune_request.training_method.simpo_gamma or 0,
        )
    else:
        raise ValueError(f"Unknown training method: {finetune_request.training_method}")

    return training_type_cls, training_method_cls


def get_model_limits(client: Together, model: str) -> FinetuneTrainingLimits:
    """
    Requests training limits for a specific model

    Args:
        model_name (str): Name of the model to get limits for

    Returns:
    FinetuneTrainingLimits: Object containing training limits for the model
    """

    response = client.get(
        "/fine-tunes/models/limits",
        cast_to=FinetuneTrainingLimits,
        options={
            "params": {"model_name": model},
        },
    )

    return response


async def async_get_model_limits(client: AsyncTogether, model: str) -> FinetuneTrainingLimits:
    """
    Requests training limits for a specific model

    Args:
        model_name (str): Name of the model to get limits for

    Returns:
    FinetuneTrainingLimits: Object containing training limits for the model
    """

    response = await client.get(
        "/fine-tunes/models/limits",
        cast_to=FinetuneTrainingLimits,
        options={
            "params": {"model_name": model},
        },
    )

    return response
