"""Utility functions for jig CLI commands."""

from __future__ import annotations

from typing import Any
from datetime import datetime, timezone
from collections import defaultdict


def _format_age(timestamp_str: str | None) -> str:
    """Format timestamp as human-readable age (e.g., '5m', '2h', '3d')"""
    if not timestamp_str:
        return "-"
    try:
        # Parse ISO8601 timestamp
        ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = now - ts
        seconds = int(delta.total_seconds())

        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m"
        elif seconds < 86400:
            return f"{seconds // 3600}h"
        else:
            return f"{seconds // 86400}d"
    except (ValueError, TypeError):
        return "-"


def _format_timestamp(timestamp_str: str | None) -> str:
    """Format ISO timestamp for display"""
    if not timestamp_str:
        return "-"
    try:
        ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return ts.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return timestamp_str or "-"


def _format_deployment_status(data: dict[str, Any]) -> str:
    """Format deployment status for CLI display"""
    lines: list[str] = []

    # Header section
    name = data.get("name", "-")
    dep_id = data.get("id", "-")
    status = data.get("status", "-")
    min_rep = data.get("min_replicas", 0)
    max_rep = data.get("max_replicas", 0)
    desired = data.get("desired_replicas", 0)
    ready = data.get("ready_replicas", 0)
    created = _format_timestamp(data.get("created_at"))
    updated = _format_timestamp(data.get("updated_at"))

    lines.append(f"{name}, id: {dep_id}")
    lines.append(f"status: {status}")
    lines.append(f"min/max replicas: {min_rep}/{max_rep}")
    lines.append(f"desired/ready replicas: {desired}/{ready}")

    # Autoscaling
    autoscaling = data.get("autoscaling")
    if autoscaling:
        profile = autoscaling.get("profile", "-")
        target_value = autoscaling.get("targetValue", "-")
        lines.append(f"autoscaling: {profile}, target={target_value}")
    else:
        lines.append("autoscaling: disabled")

    lines.append(f"created/updated: {created} / {updated}")

    # Settings section
    lines.append("")
    lines.append("= settings =")

    # Image
    image = data.get("image", "-")
    lines.append(image)

    # Volumes
    volumes = data.get("volumes") or []
    if volumes:
        vol_strs = [f"{v.get('name')}:{v.get('mount_path')}" for v in volumes]
        lines.append(f"volumes: {', '.join(vol_strs)}")
    else:
        lines.append("volumes: none")

    # Secrets (env vars from secrets)
    env_vars = data.get("environment_variables") or []
    secrets = [e.get("value_from_secret") for e in env_vars if e.get("value_from_secret")]
    if secrets:
        lines.append(f"secrets: {', '.join(secrets)}")
    else:
        lines.append("secrets: none")

    # Resources
    gpu_type = data.get("gpu_type", "-")
    gpu_count = data.get("gpu_count", 0)
    cpu = data.get("cpu", "-")
    memory = data.get("memory", "-")
    storage = data.get("storage", "-")
    lines.append(f"gpu: {gpu_count}x {gpu_type}, cpu: {cpu}, memory: {memory}GB, storage: {storage}MB")

    # Port, command, args, health_check
    port = data.get("port", "-")
    command = data.get("command") or []
    args = data.get("args") or []
    health_check = data.get("health_check_path", "-")
    cmd_str = " ".join(command) if command else "-"
    args_str = " ".join(args) if args else "-"
    lines.append(f"port: {port}, command: {cmd_str}, args: {args_str}, health_check_path: {health_check}")

    # Environment variables (non-secret)
    plain_env = {e.get("name"): e.get("value") for e in env_vars if e.get("value") is not None}
    if plain_env:
        env_str = ", ".join(f"{k}={v}" for k, v in plain_env.items())
        lines.append(f"environment: {env_str}")
    else:
        lines.append("environment: none")

    # Detailed status section
    replica_events = data.get("replica_events") or {}
    if replica_events:
        lines.append("")
        lines.append("= detailed status =")

        # Group replicas by image
        by_image: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
        for replica_name, replica_info in replica_events.items():
            img = replica_info.get("image", "unknown")
            # Extract just the tag from image if it's a full path
            if ":" in img:
                img = img.split(":")[-1]
                # Handle digest format (image@sha256:...)
                if "@" in img:
                    img = img.split("@")[0]
            by_image[img].append((replica_name, replica_info))

        for img, replicas in sorted(by_image.items()):
            lines.append(f"{img}:")
            for replica_name, replica_info in replicas:
                status_str = replica_info.get("replica_status", "Unknown")
                reason = replica_info.get("replica_status_reason")
                if reason and reason != status_str:
                    status_str = f"{status_str}:{reason}"

                age = _format_age(replica_info.get("replica_ready_since"))

                lines.append(f"    {replica_name}: {status_str}, Age {age}")

    return "\n".join(lines)
