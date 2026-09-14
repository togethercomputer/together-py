from __future__ import annotations

import re
from typing import Optional
from dataclasses import dataclass

from together.lib.cli.utils.config import CLIConfigParameter
from together.types.beta.models.config import Config
from together.types.beta.endpoints.inference_instance_type import InferenceInstanceType


@dataclass(frozen=True)
class HardwarePricing:
    """Resolved GPU label and hourly cost for a deploy preview."""

    gpu_label: str
    estimated_price_label: str
    hardware_id: str
    price_cents_per_hour: int


def selector_value(config: Config, key: str) -> Optional[str]:
    for selector in config.selectors or []:
        if selector.key == key:
            return selector.value
    return None


def hardware_from_selectors(config: Config) -> Optional[str]:
    """Build an instance-type name from accelerator selectors.

    Matches the backend / web convention: ``accelerator_count`` + ``accelerator_type``
    → ``{count}x{type}`` (e.g. ``1xnvidia-h100-80gb``).
    """
    accel_type = selector_value(config, "accelerator_type")
    accel_count = selector_value(config, "accelerator_count")
    if not accel_type or not accel_count:
        return None
    return f"{accel_count}x{accel_type}"


def prettify_hardware(hardware: str) -> str:
    """Human-readable GPU label, e.g. ``1xnvidia-h100-80gb`` → ``1x H100 80GB``."""
    match = re.search(r"(\d+)x(.*)", hardware)
    if not match:
        return hardware.replace("_", " ").title()
    count, hw_type = match.groups()
    parts = [part for part in hw_type.split("-") if part]
    if parts and parts[0].lower() in {"nvidia", "amd"}:
        parts = parts[1:]
    if not parts:
        return f"{count}x {hw_type.upper()}"
    return f"{count}x {' '.join(parts).upper()}"


def format_gpu_label(instance: InferenceInstanceType) -> str:
    # Prefer the deployable name (`1xnvidia-h100-80gb` → `1x H100 80GB`) so the
    # preview matches `tg beta endpoints ls` hardware formatting.
    if instance.name:
        return prettify_hardware(instance.name)
    gpu_type = instance.gpu_type or ""
    gpu_type = re.sub(r"(?i)^nvidia-", "", gpu_type)
    gpu_type = gpu_type.replace("-", " ").strip()
    if instance.gpu_count and gpu_type:
        return f"{instance.gpu_count}x {gpu_type.upper()}"
    return instance.id


def format_estimated_price(
    price_cents_per_hour: int,
    *,
    min_replicas: int,
    max_replicas: int,
) -> str:
    """Hourly cost at min/max replica bounds (collapses when they match)."""
    min_replicas = max(0, min_replicas)
    max_replicas = max(min_replicas, max_replicas)
    min_dollars = (price_cents_per_hour * min_replicas) / 100
    max_dollars = (price_cents_per_hour * max_replicas) / 100
    if max_dollars > min_dollars:
        return f"${min_dollars:.2f}/hr - ${max_dollars:.2f}/hr"
    return f"${min_dollars:.2f}/hr"


def find_instance_type(
    instance_types: list[InferenceInstanceType],
    *,
    hardware_id: str,
) -> Optional[InferenceInstanceType]:
    """Match an instance type by deployable name (preferred) or id."""
    for instance in instance_types:
        if instance.name == hardware_id or instance.id == hardware_id:
            return instance
    # Tolerate missing vendor prefix: ``1xh100-80gb`` ↔ ``1xnvidia-h100-80gb``.
    normalized = hardware_id.lower().replace("nvidia-", "")
    for instance in instance_types:
        candidate = (instance.name or "").lower().replace("nvidia-", "")
        if candidate == normalized:
            return instance
    return None


async def ensure_config_with_selectors(config: CLIConfigParameter, model_config: Config) -> Config:
    """Fetch the full config body when the resolved stub lacks selectors."""
    if model_config.selectors:
        return model_config
    if not model_config.id or not model_config.project_id:
        return model_config
    try:
        return await config.client.beta.models.configs.retrieve(
            model_config.id,
            project_id=model_config.project_id,
        )
    except Exception:
        return model_config


async def resolve_hardware_pricing(
    config: CLIConfigParameter,
    model_config: Config,
    *,
    min_replicas: int,
    max_replicas: int,
) -> Optional[HardwarePricing]:
    """Look up GPU info and estimated hourly price for a deployment config."""
    model_config = await ensure_config_with_selectors(config, model_config)
    hardware_id = hardware_from_selectors(model_config)
    if not hardware_id:
        return None

    try:
        catalog = await config.client.beta.endpoints.hardware.list()
    except Exception:
        # Preview should not block deploy when the catalog is unavailable.
        return HardwarePricing(
            gpu_label=prettify_hardware(hardware_id),
            estimated_price_label="unavailable",
            hardware_id=hardware_id,
            price_cents_per_hour=0,
        )

    instance = find_instance_type(catalog.data or [], hardware_id=hardware_id)
    if instance is None:
        return HardwarePricing(
            gpu_label=prettify_hardware(hardware_id),
            estimated_price_label="unavailable",
            hardware_id=hardware_id,
            price_cents_per_hour=0,
        )

    return HardwarePricing(
        gpu_label=format_gpu_label(instance),
        estimated_price_label=format_estimated_price(
            instance.price_cents_per_hour,
            min_replicas=min_replicas,
            max_replicas=max_replicas,
        ),
        hardware_id=instance.name or hardware_id,
        price_cents_per_hour=instance.price_cents_per_hour,
    )
