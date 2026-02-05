"""Utility functions for jig CLI commands."""

from __future__ import annotations

from datetime import datetime, timezone
from collections import defaultdict

from together.types.beta.deployment import Volume, Deployment, ReplicaEvents, EnvironmentVariable


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


def format_deployment_status(deployment: Deployment) -> str:
    """Format deployment status for CLI display"""
    lines: list[str] = []

    # Header section
    name = deployment.name
    dep_id = deployment.id
    status = deployment.status
    min_rep = deployment.min_replicas
    max_rep = deployment.max_replicas
    desired = deployment.desired_replicas
    ready = deployment.ready_replicas
    created = _format_timestamp(deployment.created_at)
    updated = _format_timestamp(deployment.updated_at)

    lines.append(f"{name}, id: {dep_id}")
    lines.append(f"status: {status}")
    lines.append(f"min/max replicas: {min_rep}/{max_rep}")
    lines.append(f"desired/ready replicas: {desired}/{ready}")

    # Autoscaling
    autoscaling = deployment.autoscaling
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
    image = deployment.image or "-"
    lines.append(image)

    # Volumes
    volumes: list[Volume] | None = deployment.volumes
    if volumes:
        vol_strs = [f"{v.name}:{v.mount_path}" for v in volumes]
        lines.append(f"volumes: {', '.join(vol_strs)}")
    else:
        lines.append("volumes: none")

    # Secrets (env vars from secrets)
    env_vars: list[EnvironmentVariable] = deployment.environment_variables or []
    secrets: list[str] = [e.value_from_secret for e in env_vars if e.value_from_secret]
    if secrets:
        lines.append(f"secrets: {', '.join(secrets)}")
    else:
        lines.append("secrets: none")

    # Resources
    gpu_type = deployment.gpu_type
    gpu_count = deployment.gpu_count
    cpu = deployment.cpu
    memory = deployment.memory
    storage = deployment.storage
    lines.append(f"gpu: {gpu_count}x {gpu_type}, cpu: {cpu}, memory: {memory}GB, storage: {storage}MB")

    # Port, command, args, health_check
    port = deployment.port
    command: list[str] | None = deployment.command
    args: list[str] | None = deployment.args
    health_check = deployment.health_check_path
    cmd_str = " ".join(command) if command else "-"
    args_str = " ".join(args) if args else "-"
    lines.append(f"port: {port}, command: {cmd_str}, args: {args_str}, health_check_path: {health_check}")

    # Environment variables (non-secret)
    plain_env = {e.name: e.value for e in env_vars if e.value is not None}
    if plain_env:
        env_str = ", ".join(f"{k}={v}" for k, v in plain_env.items())
        lines.append(f"environment: {env_str}")
    else:
        lines.append("environment: none")

    # Detailed status section
    replica_events = deployment.replica_events
    if replica_events:
        lines.append("")
        lines.append("= detailed status =")

        # Group replicas by image
        by_image: dict[str, list[tuple[str, ReplicaEvents]]] = defaultdict(list)
        for replica_name, replica_info in replica_events.items():
            img: str = replica_info.image or "Unknown"
            # Extract just the tag from image if it's a full path
            if ":" in img:
                img = img.split(":")[-1]
                # Handle digest format (image@sha256:...)
                if "@" in img:
                    img = img.split("@")[0]
            by_image[img].append((replica_name, replica_info))

        # Get latest revision ID from env vars
        latest_revision = None
        for e in env_vars:
            if e.name == "TOGETHER_DEPLOYMENT_REVISION_ID":
                latest_revision = e.value
                break

        for img, replicas in sorted(by_image.items()):
            lines.append(f"image: {img}:")
            for replica_name, replica_info in replicas:
                status_str = replica_info.replica_status or "Unknown"
                reason = replica_info.replica_status_reason
                if reason and reason != status_str:
                    status_str = f"{status_str}:{reason}"

                # Show volume preload status if loading
                preload_status = replica_info.volume_preload_status
                preload_completed = replica_info.volume_preload_completed_at
                if preload_status and not preload_completed:
                    status_str = f"{status_str} (Loading volume contents)"

                age = _format_age(replica_info.replica_ready_since)
                revision_id = replica_info.revision_id
                is_latest = " (latest)" if revision_id and revision_id == latest_revision else ""

                lines.append(
                    f"    {replica_name}: {status_str}, Age {age}, Rev {revision_id if revision_id else '-'}{is_latest}"
                )

    return "\n".join(lines)
