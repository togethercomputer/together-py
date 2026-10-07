"""Immutable loss wire contracts and runtime validation helpers."""

from __future__ import annotations

import types
import warnings
from typing import Any, cast, get_args, get_origin, get_type_hints
from dataclasses import replace, dataclass
from collections.abc import Set as AbstractSet, Mapping
from typing_extensions import Required

from ._request_types import Sample, LossConfig
from ....types.beta.rl import loss_config_param
from ....types.beta.rl.loss_type import LossType


@dataclass(frozen=True)
class InputSpec:
    """Required and optional ``loss_fn_inputs`` keys for one request shape."""

    required_inputs: frozenset[str]
    optional_inputs: frozenset[str]


@dataclass(frozen=True)
class LossSpec(InputSpec):
    """The wire contract for one loss type.

    The ``*_loss_config`` and ``*_config`` key sets are derived from the generated
    ``LossConfig`` TypedDicts, so a spec change reaches this table through codegen.
    The tensor-input key sets are hand-maintained against the server's prose contract.
    """

    wire_type: LossType
    params_key: str | None
    required_loss_config: frozenset[str]
    optional_loss_config: frozenset[str]
    required_params: frozenset[str]
    optional_params: frozenset[str]


INPUT_DTYPES: Mapping[str, frozenset[str]] = types.MappingProxyType(
    {
        "target_tokens": frozenset({"int64"}),
        "logprobs": frozenset({"float32"}),
        "advantages": frozenset({"float32"}),
        "reference_logprobs": frozenset({"float32"}),
        "weights": frozenset({"int64", "float32"}),
        "mask": frozenset({"int64", "float32"}),
    }
)

_NO_KEYS: frozenset[str] = frozenset()


def _unwrap_required(hint: Any) -> Any:
    """Peel a ``Required[...]`` marker off a generated annotation.

    ``get_type_hints`` rejects a bare ``Required[T]``, so a params key the spec promotes
    to required must be unwrapped before its own shape can be resolved.
    """
    return get_args(hint)[0] if get_origin(hint) is Required else hint


def _split_required(hints: Mapping[str, Any]) -> tuple[frozenset[str], frozenset[str]]:
    """Split one generated TypedDict's resolved hints into required and optional keys."""
    required = frozenset(key for key, hint in hints.items() if get_origin(hint) is Required)
    return required, frozenset(hints) - required


_LOSS_CONFIG_HINTS = get_type_hints(loss_config_param.LossConfig, include_extras=True)
_LOSS_CONFIG_REQUIRED, _ = _split_required(_LOSS_CONFIG_HINTS)
_POLICY_REQUIRED_INPUTS = frozenset({"target_tokens", "logprobs", "advantages"})
_POLICY_OPTIONAL_INPUTS = frozenset({"weights", "mask"})
# The one operation that carries no loss config, so no loss declares its inputs.
CUSTOM_FORWARD_BACKWARD_INPUTS = InputSpec(
    required_inputs=frozenset({"target_tokens"}),
    optional_inputs=frozenset({"weights", "mask"}),
)


def _make_spec(
    wire_type: LossType,
    *,
    params_key: str | None = None,
    required_inputs: frozenset[str] = _POLICY_REQUIRED_INPUTS,
    optional_inputs: frozenset[str] = _POLICY_OPTIONAL_INPUTS,
) -> LossSpec:
    """Build one loss contract, reading its config keys off the generated TypedDicts."""
    if params_key is None:
        config_key = required_params = optional_params = _NO_KEYS
    else:
        config_key = frozenset({params_key})
        params_shape = _unwrap_required(_LOSS_CONFIG_HINTS[params_key])
        required_params, optional_params = _split_required(get_type_hints(params_shape, include_extras=True))
    # A params key the caller cannot omit is one whose generated shape has a required member.
    # No loss today declares an optional params object with a required member; if one ever
    # ships ("if you send it, set X"), this would demand it unconditionally.
    params_required = bool(required_params)
    required_loss_config, optional_loss_config = (config_key, _NO_KEYS) if params_required else (_NO_KEYS, config_key)
    return LossSpec(
        wire_type=wire_type,
        params_key=params_key,
        required_loss_config=_LOSS_CONFIG_REQUIRED | required_loss_config,
        optional_loss_config=optional_loss_config,
        required_params=required_params,
        optional_params=optional_params,
        required_inputs=required_inputs,
        optional_inputs=optional_inputs,
    )


LOSS_SPECS: Mapping[LossType, LossSpec] = types.MappingProxyType(
    {
        "LOSS_TYPE_CROSS_ENTROPY": _make_spec(
            "LOSS_TYPE_CROSS_ENTROPY",
            params_key="cross_entropy_params",
            required_inputs=frozenset({"target_tokens", "weights"}),
            optional_inputs=_NO_KEYS,
        ),
        "LOSS_TYPE_GRPO": _make_spec(
            "LOSS_TYPE_GRPO",
            params_key="grpo_params",
            optional_inputs=_POLICY_OPTIONAL_INPUTS | frozenset({"reference_logprobs"}),
        ),
        "LOSS_TYPE_IMPORTANCE_SAMPLING": _make_spec("LOSS_TYPE_IMPORTANCE_SAMPLING"),
        "LOSS_TYPE_PPO": _make_spec(
            "LOSS_TYPE_PPO",
            params_key="ppo_params",
        ),
        "LOSS_TYPE_CISPO": _make_spec(
            "LOSS_TYPE_CISPO",
            params_key="cispo_params",
        ),
        "LOSS_TYPE_DPPO": _make_spec(
            "LOSS_TYPE_DPPO",
            params_key="dppo_params",
        ),
        "LOSS_TYPE_DRO": _make_spec(
            "LOSS_TYPE_DRO",
            params_key="dro_params",
        ),
    }
)


def validate_keys(
    label: str,
    keys: AbstractSet[str],
    *,
    required: AbstractSet[str],
    optional: AbstractSet[str],
) -> None:
    """Validate a mapping's keys against one generated wire shape.

    Raises:
        ValueError: If ``keys`` carries a key outside the shape or misses a required one.
    """
    accepted = required | optional
    unknown = sorted(keys - accepted)
    if unknown:
        raise ValueError(f"Unsupported keys in {label}: {unknown}; accepted keys are {sorted(accepted)}")
    _require_keys(label, keys, required=required)


def _require_keys(label: str, keys: AbstractSet[str], *, required: AbstractSet[str]) -> None:
    missing = sorted(required - keys)
    if missing:
        raise ValueError(f"{label} must include {missing}")


def validate_input_keys(label: str, keys: AbstractSet[str], inputs: InputSpec) -> None:
    """Check a ``loss_fn_inputs`` key set against the inputs one request shape declares.

    A missing required key is always the caller's error. An undeclared key is not: the
    wire shape is an open ``map<string, TensorData>``, so a key this table has not heard
    of is as likely to be a server input newer than the SDK as it is to be a typo. Warn
    and forward it rather than making every new server input wait on an SDK release.

    Raises:
        ValueError: If a key ``inputs`` requires is missing. ``label`` names the
            offending sample or datum in the message.
    """
    if "weights" in keys and "mask" in keys:
        raise ValueError(f"{label} cannot contain both weights and mask")
    accepted = inputs.required_inputs | inputs.optional_inputs
    unknown = sorted(keys - accepted)
    if unknown:
        # stacklevel=1 on purpose: this is reached from two different call depths (the
        # native submitters and the tinker converters), and the native path runs inside an
        # event-loop task, so no fixed value points at user code. The message deliberately
        # omits `label`: with the dedup key being this line plus the message text, a
        # batch- and path-invariant message warns once per process per unknown-key set
        # rather than once per sample — and once total when the tinker converters and the
        # shared submitter both see the same keys.

        warnings.warn(
            f"Unsupported loss_fn_inputs keys {unknown}; accepted keys are {sorted(accepted)}."
            " Forwarding them to the server.",
            UserWarning,
            stacklevel=1,
        )
    _require_keys(label, keys, required=inputs.required_inputs)


def validate_loss_config(loss: LossConfig) -> LossSpec:
    """Validate a selected loss config and return its immutable wire contract.

    Raises:
        ValueError: If the loss type is unsupported or the config's keys do not
            match the shape that loss declares.
    """
    loss_mapping = cast("Mapping[str, object]", loss)
    wire_type = cast("LossType", loss_mapping.get("type"))
    if wire_type not in LOSS_SPECS:
        raise ValueError(f"Unsupported loss type {wire_type!r}; expected one of {sorted(LOSS_SPECS)}")
    spec = LOSS_SPECS[wire_type]
    label = f"LossConfig for {wire_type!r}"
    validate_keys(
        label,
        loss_mapping.keys(),
        required=spec.required_loss_config,
        optional=spec.optional_loss_config,
    )

    if spec.params_key is not None and spec.params_key in loss_mapping:
        params = loss_mapping[spec.params_key]
        if not isinstance(params, Mapping):
            raise ValueError(f"{label}[{spec.params_key!r}] must be a mapping")
        params = cast("Mapping[str, object]", params)
        validate_keys(
            f"{label}[{spec.params_key!r}]",
            params.keys(),
            required=spec.required_params,
            optional=spec.optional_params,
        )
    if wire_type == "LOSS_TYPE_GRPO" and loss.get("grpo_params", {}).get("beta", 0) > 0:
        spec = replace(
            spec,
            required_inputs=spec.required_inputs | {"reference_logprobs"},
            optional_inputs=spec.optional_inputs - {"reference_logprobs"},
        )
    return spec


def validate_sample(sample: Sample, inputs: InputSpec, *, label: str) -> None:
    """Validate one sample's generic loss tensor map.

    Raises:
        ValueError: If ``loss_fn_inputs`` is not a mapping of tensor mappings, misses
            a key ``inputs`` requires, or carries a tensor with a disallowed dtype.
    """
    sample_mapping = cast("Mapping[str, object]", sample)
    loss_fn_inputs = sample_mapping.get("loss_fn_inputs")
    if not isinstance(loss_fn_inputs, Mapping):
        raise ValueError(f"{label}.loss_fn_inputs must be a mapping")
    loss_fn_inputs = cast("Mapping[str, object]", loss_fn_inputs)
    validate_input_keys(f"{label}.loss_fn_inputs", loss_fn_inputs.keys(), inputs)
    for key, tensor in loss_fn_inputs.items():
        if not isinstance(tensor, Mapping):
            raise ValueError(f"{label}.loss_fn_inputs[{key!r}] must be a tensor mapping")
        tensor_mapping = cast("Mapping[str, object]", tensor)
        dtype = tensor_mapping.get("dtype")
        allowed_dtypes = INPUT_DTYPES.get(key)
        if allowed_dtypes is None:
            continue
        if dtype not in allowed_dtypes:
            raise ValueError(
                f"{label}.loss_fn_inputs[{key!r}].dtype must be one of {sorted(allowed_dtypes)}, got {dtype!r}"
            )
