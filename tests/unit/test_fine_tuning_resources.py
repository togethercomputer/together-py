from typing import Union, Literal, Optional

import pytest

from together.lib.types.fine_tuning import (
    FullTrainingType,
    LoRATrainingType,
    TrainingMethodSFT,
)
from together.lib.resources.fine_tuning import create_finetune_request
from together.types.finetune_model_limits import (
    FullTraining,
    LoraTraining,
    FinetuneModelLimits,
)

_MODEL_NAME = "meta-llama/Meta-Llama-3.1-8B-Instruct-Reference"
_TRAINING_FILE = "file-7dbce5e9-7993-4520-9f3e-a7ece6c39d84"
_VALIDATION_FILE = "file-7dbce5e9-7553-4520-9f3e-a7ece6c39d84"
_FROM_CHECKPOINT = "ft-12345678-1234-1234-1234-1234567890ab"

_DEFAULT_LORA_TRAINING = LoraTraining(
    max_batch_size=128,
    max_batch_size_dpo=64,
    min_batch_size=8,
    max_rank=64,
    target_modules=["q", "k", "v", "o", "mlp"],
)
_DEFAULT_FULL_TRAINING = FullTraining(
    max_batch_size=96,
    max_batch_size_dpo=48,
    min_batch_size=8,
)


def _make_model_limits(
    *,
    full_training: Optional[FullTraining] = _DEFAULT_FULL_TRAINING,
    lora_training: LoraTraining = _DEFAULT_LORA_TRAINING,
) -> FinetuneModelLimits:
    return FinetuneModelLimits(
        model_name=_MODEL_NAME,
        default_gradient_accumulation_steps=1,
        max_num_epochs=20,
        max_num_checkpoints=10,
        max_num_evals=10,
        max_learning_rate=1.0,
        min_learning_rate=1e-6,
        merge_output_lora=True,
        supports_full_training=full_training is not None,
        supports_reasoning=False,
        supports_tools=False,
        supports_vision=False,
        full_training=full_training,
        lora_training=lora_training,
        max_seq_length_sft=4096,
        max_seq_length_dpo=4096,
        min_max_seq_length=1024,
    )


_MODEL_LIMITS = _make_model_limits()


def test_full_training_request():
    request, _, _ = create_finetune_request(
        model_limits=_MODEL_LIMITS,
        model=_MODEL_NAME,
        training_file=_TRAINING_FILE,
        lora=False,
    )

    assert isinstance(request.training_type, FullTrainingType)
    assert request.training_type.type == "Full"
    assert request.batch_size == "max"


def test_simple_request():
    request, _, _ = create_finetune_request(
        model_limits=_MODEL_LIMITS,
        model=_MODEL_NAME,
        training_file=_TRAINING_FILE,
    )

    assert request.model == _MODEL_NAME
    assert request.training_file == _TRAINING_FILE
    assert request.learning_rate > 0
    assert request.n_epochs > 0
    assert request.warmup_ratio == 0.0
    # When lora is not specified, training_type is None because the backend decides.
    assert request.training_type is None
    assert request.batch_size == "max"


def test_validation_file():
    request, _, _ = create_finetune_request(
        model_limits=_MODEL_LIMITS,
        model=_MODEL_NAME,
        training_file=_TRAINING_FILE,
        validation_file=_VALIDATION_FILE,
    )

    assert request.training_file == _TRAINING_FILE
    assert request.validation_file == _VALIDATION_FILE


def test_no_training_file():
    with pytest.raises(TypeError, match="missing 1 required positional argument: 'training_file'"):
        _ = create_finetune_request(  # type: ignore
            model_limits=_MODEL_LIMITS,
            model=_MODEL_NAME,
        )


def test_lora_request():
    request, _, _ = create_finetune_request(
        model_limits=_MODEL_LIMITS,
        model=_MODEL_NAME,
        training_file=_TRAINING_FILE,
        lora=True,
    )

    assert isinstance(request.training_type, LoRATrainingType)
    assert request.training_type.type == "Lora"
    assert request.training_type.lora_r == _MODEL_LIMITS.lora_training.max_rank
    assert request.training_type.lora_alpha == _MODEL_LIMITS.lora_training.max_rank * 2
    assert request.training_type.lora_dropout == 0.0
    assert request.training_type.lora_trainable_modules == "all-linear"
    assert request.batch_size == "max"


@pytest.mark.parametrize("lora_dropout", [-1, 0, 0.5, 1.0, 10.0])
def test_lora_request_with_lora_dropout(lora_dropout: float):
    if 0 <= lora_dropout < 1:
        request, _, _ = create_finetune_request(
            model_limits=_MODEL_LIMITS,
            model=_MODEL_NAME,
            training_file=_TRAINING_FILE,
            lora=True,
            lora_dropout=lora_dropout,
        )
        assert isinstance(request.training_type, LoRATrainingType)
        assert request.training_type.lora_dropout == lora_dropout
    else:
        with pytest.raises(
            ValueError,
            match=r"LoRA dropout must be in \[0, 1\) range.",
        ):
            create_finetune_request(
                model_limits=_MODEL_LIMITS,
                model=_MODEL_NAME,
                training_file=_TRAINING_FILE,
                lora=True,
                lora_dropout=lora_dropout,
            )


def test_dpo_request_lora():
    request, _, _ = create_finetune_request(
        model_limits=_MODEL_LIMITS,
        model=_MODEL_NAME,
        training_file=_TRAINING_FILE,
        training_method="dpo",
        lora=True,
    )

    assert isinstance(request.training_type, LoRATrainingType)
    assert request.training_type.type == "Lora"
    assert request.training_type.lora_r == _MODEL_LIMITS.lora_training.max_rank
    assert request.training_type.lora_alpha == _MODEL_LIMITS.lora_training.max_rank * 2
    assert request.training_type.lora_dropout == 0.0
    assert request.training_type.lora_trainable_modules == "all-linear"
    assert request.batch_size == "max"


def test_dpo_request():
    request, _, _ = create_finetune_request(
        model_limits=_MODEL_LIMITS,
        model=_MODEL_NAME,
        training_file=_TRAINING_FILE,
        training_method="dpo",
        lora=False,
    )

    assert isinstance(request.training_type, FullTrainingType)
    assert request.training_type.type == "Full"
    assert request.batch_size == "max"


def test_from_checkpoint_request():
    request, _, _ = create_finetune_request(
        model_limits=_MODEL_LIMITS,
        training_file=_TRAINING_FILE,
        from_checkpoint=_FROM_CHECKPOINT,
    )

    assert request.model is None
    assert request.from_checkpoint == _FROM_CHECKPOINT


def test_both_from_checkpoint_model_name():
    with pytest.raises(
        ValueError,
        match="You must specify either a model or a checkpoint to start a job from, not both",
    ):
        _ = create_finetune_request(
            model_limits=_MODEL_LIMITS,
            model=_MODEL_NAME,
            training_file=_TRAINING_FILE,
            from_checkpoint=_FROM_CHECKPOINT,
        )


def test_no_from_checkpoint_no_model_name():
    with pytest.raises(ValueError, match="You must specify either a model or a checkpoint"):
        _ = create_finetune_request(
            model_limits=_MODEL_LIMITS,
            training_file=_TRAINING_FILE,
        )


@pytest.mark.parametrize("batch_size", [256, 1])
@pytest.mark.parametrize("use_lora", [False, True])
def test_batch_size_limit(batch_size: int, use_lora: bool):
    model_limits = _MODEL_LIMITS.full_training if not use_lora else _MODEL_LIMITS.lora_training
    assert model_limits is not None
    max_batch_size = model_limits.max_batch_size
    min_batch_size = model_limits.min_batch_size

    if batch_size > max_batch_size:
        error_message = (
            f"Requested batch size of {batch_size} is higher that the maximum allowed value of {max_batch_size}"
        )
        with pytest.raises(ValueError, match=error_message):
            _ = create_finetune_request(
                model_limits=_MODEL_LIMITS,
                model=_MODEL_NAME,
                training_file=_TRAINING_FILE,
                batch_size=batch_size,
                lora=use_lora,
            )

    if batch_size < min_batch_size:
        error_message = (
            f"Requested batch size of {batch_size} is lower that the minimum allowed value of {min_batch_size}"
        )
        with pytest.raises(ValueError, match=error_message):
            _ = create_finetune_request(
                model_limits=_MODEL_LIMITS,
                model=_MODEL_NAME,
                training_file=_TRAINING_FILE,
                batch_size=batch_size,
                lora=use_lora,
            )


def test_non_full_model():
    with pytest.raises(ValueError, match="Full training is not supported for the selected model."):
        _ = create_finetune_request(
            model_limits=_make_model_limits(full_training=None),
            model=_MODEL_NAME,
            training_file=_TRAINING_FILE,
            lora=False,
        )


@pytest.mark.parametrize("warmup_ratio", [-1.0, 2.0])
def test_bad_warmup(warmup_ratio: float):
    with pytest.raises(ValueError, match="Warmup ratio should be between 0 and 1"):
        _ = create_finetune_request(
            model_limits=_MODEL_LIMITS,
            model=_MODEL_NAME,
            training_file=_TRAINING_FILE,
            warmup_ratio=warmup_ratio,
        )


@pytest.mark.parametrize("min_lr_ratio", [-1.0, 2.0])
def test_bad_min_lr_ratio(min_lr_ratio: float):
    with pytest.raises(ValueError, match="Min learning rate ratio should be between 0 and 1"):
        _ = create_finetune_request(
            model_limits=_MODEL_LIMITS,
            model=_MODEL_NAME,
            training_file=_TRAINING_FILE,
            min_lr_ratio=min_lr_ratio,
        )


@pytest.mark.parametrize("max_grad_norm", [-1.0, -0.01])
def test_bad_max_grad_norm(max_grad_norm: float):
    with pytest.raises(ValueError, match="Max gradient norm should be non-negative"):
        _ = create_finetune_request(
            model_limits=_MODEL_LIMITS,
            model=_MODEL_NAME,
            training_file=_TRAINING_FILE,
            max_grad_norm=max_grad_norm,
        )


@pytest.mark.parametrize("weight_decay", [-1.0, -0.01])
def test_bad_weight_decay(weight_decay: float):
    with pytest.raises(ValueError, match="Weight decay should be non-negative"):
        _ = create_finetune_request(
            model_limits=_MODEL_LIMITS,
            model=_MODEL_NAME,
            training_file=_TRAINING_FILE,
            weight_decay=weight_decay,
        )


def test_bad_training_method():
    with pytest.raises(ValueError, match="training_method must be one of .*"):
        _ = create_finetune_request(
            model_limits=_MODEL_LIMITS,
            model=_MODEL_NAME,
            training_file=_TRAINING_FILE,
            training_method="NON_SFT",
        )


@pytest.mark.parametrize("train_on_inputs", [True, False, "auto", None])
def test_train_on_inputs_for_sft(train_on_inputs: Union[bool, Literal["auto"], None]):
    request, _, _ = create_finetune_request(
        model_limits=_MODEL_LIMITS,
        model=_MODEL_NAME,
        training_file=_TRAINING_FILE,
        training_method="sft",
        train_on_inputs=train_on_inputs,
    )
    assert isinstance(request.training_method, TrainingMethodSFT)
    assert request.training_method.method == "sft"
    if isinstance(train_on_inputs, bool):
        assert request.training_method.train_on_inputs is train_on_inputs
    else:
        assert request.training_method.train_on_inputs == "auto"


def test_train_on_inputs_not_supported_for_dpo():
    with pytest.raises(ValueError, match="train_on_inputs is only supported for SFT training"):
        _ = create_finetune_request(
            model_limits=_MODEL_LIMITS,
            model=_MODEL_NAME,
            training_file=_TRAINING_FILE,
            training_method="dpo",
            train_on_inputs=True,
        )


def test_early_stopping_request():
    request, _, _ = create_finetune_request(
        model_limits=_MODEL_LIMITS,
        model=_MODEL_NAME,
        training_file=_TRAINING_FILE,
        validation_file=_VALIDATION_FILE,
        n_evals=10,
        early_stopping_enabled=True,
        early_stopping_patience=3,
        early_stopping_min_delta=0.01,
        early_stopping_warmup_evals=2,
    )

    assert request.early_stopping_enabled is True
    assert request.early_stopping_patience == 3
    assert request.early_stopping_min_delta == 0.01
    assert request.early_stopping_warmup_evals == 2


def test_early_stopping_overrides_omitted_when_unset():
    # Only the toggle is set; the tuning knobs stay None so the server applies its defaults.
    request, _, _ = create_finetune_request(
        model_limits=_MODEL_LIMITS,
        model=_MODEL_NAME,
        training_file=_TRAINING_FILE,
        validation_file=_VALIDATION_FILE,
        n_evals=10,
        early_stopping_enabled=True,
    )

    assert request.early_stopping_enabled is True
    assert request.early_stopping_patience is None
    assert request.early_stopping_min_delta is None
    assert request.early_stopping_warmup_evals is None


@pytest.mark.parametrize(
    "patience, warmup, min_delta, n_evals, match",
    [
        (0, 1, 0.0, 10, "patience must be >= 1"),
        (2, -1, 0.0, 10, "warmup_evals must be >= 0"),
        (2, 1, -0.1, 10, "min_delta must be >= 0"),
        (2, 1, 0.0, 3, "n_evals >= patience"),  # 2 + 1 + 1 = 4 > 3
    ],
)
def test_early_stopping_invalid_config(patience: int, warmup: int, min_delta: float, n_evals: int, match: str):
    with pytest.raises(ValueError, match=match):
        _ = create_finetune_request(
            model_limits=_MODEL_LIMITS,
            model=_MODEL_NAME,
            training_file=_TRAINING_FILE,
            validation_file=_VALIDATION_FILE,
            n_evals=n_evals,
            early_stopping_enabled=True,
            early_stopping_patience=patience,
            early_stopping_min_delta=min_delta,
            early_stopping_warmup_evals=warmup,
        )
