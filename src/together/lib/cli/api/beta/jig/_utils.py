"""Utility functions for jig CLI commands."""

from __future__ import annotations

from datetime import datetime

from together.types.beta.deployment import Deployment


def _format_timestamp(timestamp_str: str | None) -> str:
    """Format ISO timestamp for display"""
    if not timestamp_str:
        return "-"
    try:
        ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return ts.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return timestamp_str or "-"


def _image_tag(image: str | None) -> str:
    if image is None:
        return "unknown"
    tag = image.rsplit(":", 1)[-1] if ":" in image else image
    if "@sha256:" in image:
        tag = f"sha256:{tag[:8]}"

    return tag


def format_deployment_status(deployment: Deployment) -> str:
    """Format deployment status for CLI display"""
    status = (
        "App:\n"
        f"  {'Name':<8}: {deployment.name} ┃ ID: {deployment.id}\n"
        f"  {'Image':<8}: {deployment.image}\n"
        f"  {'Status':<8}: {deployment.status}\n"
        f"  Created : {_format_timestamp(deployment.created_at)}"
        f" ┃ Updated : {_format_timestamp(deployment.updated_at)}\n"
    )

    if deployment.autoscaling:
        autoscaling_status = f"\n  Autoscaling: {deployment.autoscaling.get('profile', 'N/A')} {deployment.autoscaling.get('targetValue', 'N/A')}(target)\n"
        status += autoscaling_status

    replica_status = (
        "\n"
        f"  Replicas:\n"
        f"    {'Min/Max':<16}: {deployment.min_replicas}/{deployment.max_replicas}\n"
        f"    {'Ready/Desired':<16}: {deployment.ready_replicas}/{deployment.desired_replicas}\n"
    )

    status += replica_status

    config_status = (
        f"\nConfiguration:\n"
        f"  Port: {deployment.port}\n"
        f"  Command: {deployment.command}\n"
        f"  Args: {deployment.args}\n"
        f"  Health Check Path: {deployment.health_check_path}\n"
        f"  Resources: {deployment.cpu} core CPU ┃ {deployment.memory}GB Memory ┃ {deployment.storage}GB Storage \n"
    )

    if deployment.gpu_count and deployment.gpu_type:
        config_status += f"  GPU: {deployment.gpu_count}x {deployment.gpu_type}\n"

    if deployment.volumes:
        config_status += f"\n  Volumes:\n    {'NAME':<28} MOUNT_PATH\n"
        for vol in deployment.volumes:
            config_status += f"    {vol.name:<28} {vol.mount_path}\n"

    if deployment.environment_variables:
        secrets = [env for env in deployment.environment_variables if env.value_from_secret]
        env_vars = [env for env in deployment.environment_variables if not env.value_from_secret]

        if secrets:
            config_status += f"\n  Secrets: {[secret.name for secret in secrets]}\n"

        if env_vars:
            config_status += f"\n  Environment Variables:\n    {'NAME':<40} VALUE\n"
            for env in env_vars:
                config_status += f"    {env.name:<40} {env.value}\n"

    status += config_status

    if deployment.replica_events:
        events_status = "\nReplica Events:\n"
        images = set(map(lambda x: x.image or "-", deployment.replica_events.values()))
        for image in reversed(sorted(images)):
            events = filter(lambda x: ((x[1].image or "-") == image), deployment.replica_events.items())
            events_status += f"{_image_tag(image)}:\n"
            for replica_id, event in events:
                events_status += f"  {replica_id}: "

                if event.volume_preload_status and not event.volume_preload_completed_at:
                    events_status += f"Volume Preloading"
                else:
                    events_status += f"{event.replica_status}"
                    if event.replica_status == "Running":
                        events_status += f", ready since {_format_timestamp(event.replica_ready_since)}"
                events_status += "\n"

        status += events_status

    return status
