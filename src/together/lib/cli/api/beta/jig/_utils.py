"""Utility functions for jig CLI commands."""

from __future__ import annotations
from itertools import groupby
from datetime import datetime

from together.types.beta.deployment import Deployment


def _format_timestamp(ts: str | None) -> str:
    """Format ISO timestamp for display"""
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError, AttributeError):
        return timestamp_str or "-"


def _image_tag(image: str | None) -> str:
    if image is None:
        return "unknown"
    tag = image.rsplit(":", 1)[-1]
    return f"sha256:{tag[:8]}" if "sha256:" in image else tag


def format_deployment_status(d: Deployment) -> str:
    """Format d status for CLI display"""
    status = (
        "App:\n"
        f"  {'Name':<8}: {d.name} ┃ ID: {d.id}\n"
        f"  {'Image':<8}: {d.image}\n"
        f"  {'Status':<8}: {d.status}\n"
        f"  Created : {_format_timestamp(d.created_at)}"
        f" ┃ Updated : {_format_timestamp(d.updated_at)}\n"
    )

    if d.autoscaling:
        autoscaling_status = (
            f"\n  Autoscaling: {d.autoscaling.get('metric', 'N/A')} {d.autoscaling.get('target', 'N/A')}(target)\n"
        )
        status += autoscaling_status

    replica_status = (
        "\n"
        f"  Replicas:\n"
        f"    {'Min/Max':<16}: {d.min_replicas}/{d.max_replicas}\n"
        f"    {'Ready/Desired':<16}: {d.ready_replicas}/{d.desired_replicas}\n"
    )

    status += replica_status

    config_status = (
        f"\nConfiguration:\n"
        f"  Port: {d.port}\n"
        f"  Command: {d.command}\n"
        f"  Args: {d.args}\n"
        f"  Health Check Path: {d.health_check_path}\n"
        f"  Resources: {d.cpu} core CPU ┃ {d.memory}GB Memory ┃ {d.storage}GB Storage \n"
    )

    if d.gpu_count and d.gpu_type:
        config_status += f"  GPU: {d.gpu_count}x {d.gpu_type}\n"

    if d.volumes:
        config_status += f"\n  Volumes:\n    {'NAME':<28} MOUNT_PATH\n"
        for vol in d.volumes:
            config_status += f"    {vol.name:<28} {vol.mount_path}\n"

    if d.environment_variables:
        secrets = [env for env in d.environment_variables if env.value_from_secret]
        env_vars = [env for env in d.environment_variables if not env.value_from_secret]

        if secrets:
            config_status += f"\n  Secrets: {[secret.name for secret in secrets]}\n"

        if env_vars:
            config_status += f"\n  Environment Variables:\n    {'NAME':<40} VALUE\n"
            for env in env_vars:
                config_status += f"    {env.name:<40} {env.value}\n"

    status += config_status

    if d.replica_events:
        for replica in d.replica_events.values():
            replica.image = replica.image or "-"
        sorted_replicas = sorted(d.replica_events.items(), key=lambda item: item[1].image, reverse=True)
        events_status = "\nReplica Events:\n"
        for image, group in groupby(sorted_replicas, key=lambda item: item[1].image):
            events_status += f"{_image_tag(image)}:\n"
            for replica_id, replica in group:
                events_status += f"  {replica_id}: "
                if replica.volume_preload_status and not replica.volume_preload_completed_at:
                    events_status += f"Volume Preloading"
                else:
                    events_status += f"{replica.replica_status}"
                    if replica.replica_status == "Running":
                        events_status += f", ready since {_format_timestamp(replica.replica_ready_since)}"
                events_status += "\n"

        status += events_status
    return status
