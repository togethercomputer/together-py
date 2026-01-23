"""Jig - Simple deployment tool for Together AI."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import click
import httpx

from ._client import API_URL, REGISTRY_URL, APIClient
from ._config import Config
from ._helpers import (
    GENERATE_DOCKERFILE,
    AppContext,
    do_dockerfile,
    get_image,
    get_image_with_digest,
    set_secret,
    watch_job_status,
)
from ._state import State
from .secrets import secrets
from .volumes import volumes


@click.group()
@click.pass_context
@click.option("--config", "config_path", type=str, help="Configuration file path")
def jig(ctx: click.Context, config_path: str | None) -> None:
    """jig - Simple deployment tool for Together AI"""
    # Skip initialization for 'init' command
    if ctx.invoked_subcommand == "init":
        return

    # Skip initialization when showing help
    if "--help" in sys.argv:
        return

    cfg = Config.find(config_path)
    state = State.load(cfg._path.parent)

    api_key = os.getenv("TOGETHER_API_KEY", "")
    if not api_key:
        click.echo("ERROR: TOGETHER_API_KEY must be set", err=True)
        ctx.exit(1)

    client = APIClient(api_key)
    if not state.username:
        state.username = client.get_username()
        state.save()

    ctx.obj = AppContext(config=cfg, state=state, client=client, api_key=api_key)


# --- Top-level Commands ---


@jig.command()
def init() -> None:
    """Initialize jig configuration"""
    pyproject = Path("pyproject.toml")
    if pyproject.exists():
        click.echo("pyproject.toml already exists")
        return

    content = """[project]
name = "my-model"
version = "0.1.0"
dependencies = ["torch", "transformers"]

[tool.jig.image]
python_version = "3.11"
system_packages = ["git", "libglib2.0-0"]
cmd = "python app.py"

[tool.jig.deploy]
description = "My model deployment"
gpu_type = "h100-80gb"
gpu_count = 1
"""
    with open(pyproject, "w") as f:
        f.write(content)
    click.echo("\N{CHECK MARK} Created pyproject.toml")
    click.echo("  Edit the configuration and run 'together jig deploy'")


@jig.command()
@click.pass_context
def dockerfile(ctx: click.Context) -> None:
    """Generate Dockerfile"""
    app_ctx: AppContext = ctx.obj
    do_dockerfile(app_ctx.config)


@jig.command()
@click.pass_context
@click.option("--tag", default="latest", help="Image tag")
def build(ctx: click.Context, tag: str) -> None:
    """Build container image"""
    app_ctx: AppContext = ctx.obj
    image = get_image(app_ctx, tag)

    if GENERATE_DOCKERFILE:
        dockerfile_path = Path(app_ctx.config.dockerfile)
        if (
            app_ctx.config._path
            and app_ctx.config._path.exists()
            and dockerfile_path.exists()
            and app_ctx.config._path.stat().st_mtime > dockerfile_path.stat().st_mtime
        ):
            click.echo(f"\N{INFORMATION SOURCE} {app_ctx.config._path} has changed, regenerating Dockerfile")
            do_dockerfile(app_ctx.config)

        if not dockerfile_path.exists():
            do_dockerfile(app_ctx.config)

    # Copy sprocket worker if it exists
    build_dir_worker_path = Path("./.sprocket.py")
    dst = Path(__file__).parent / "sprocket" / "sprocket.py"
    try:
        shutil.copy(dst, build_dir_worker_path)
    except FileNotFoundError:
        pass

    click.echo(f"Building {image}")
    cmd = ["docker", "build", "--platform", "linux/amd64", "-t", image, "."]
    if app_ctx.config.dockerfile != "Dockerfile":
        cmd.extend(["-f", app_ctx.config.dockerfile])

    if subprocess.run(cmd).returncode != 0:
        raise click.ClickException("Build failed")

    build_dir_worker_path.unlink(missing_ok=True)
    click.echo("\N{CHECK MARK} Built")


@jig.command()
@click.pass_context
@click.option("--tag", default="latest", help="Image tag")
def push(ctx: click.Context, tag: str) -> None:
    """Push image to registry"""
    app_ctx: AppContext = ctx.obj
    image = get_image(app_ctx, tag)

    # Login
    login_cmd = f"echo {app_ctx.api_key} | docker login {REGISTRY_URL} --username user --password-stdin"
    if subprocess.run(login_cmd, shell=True, capture_output=True).returncode != 0:
        raise click.ClickException("Registry login failed")

    click.echo(f"Pushing {image}")
    if subprocess.run(["docker", "push", image]).returncode != 0:
        raise click.ClickException("Push failed")
    click.echo("\N{CHECK MARK} Pushed")


@jig.command()
@click.pass_context
@click.option("--tag", default="latest", help="Image tag")
@click.option("--build-only", is_flag=True, help="Build and push only")
@click.option("--image", "existing_image", help="Use existing image (skip build/push)")
def deploy(ctx: click.Context, tag: str, build_only: bool, existing_image: str | None) -> dict[str, Any] | None:
    """Deploy model"""
    app_ctx: AppContext = ctx.obj

    if existing_image:
        deployment_image = existing_image
    else:
        # Build and push
        ctx.invoke(build, tag=tag)
        ctx.invoke(push, tag=tag)
        deployment_image = get_image_with_digest(app_ctx, tag)

    if build_only:
        click.echo("\N{CHECK MARK} Build complete (--build-only)")
        return None

    deploy_data: dict[str, Any] = {
        "name": app_ctx.config.model_name,
        "description": app_ctx.config.deploy.description,
        "image": deployment_image,
        "min_replicas": app_ctx.config.deploy.min_replicas,
        "max_replicas": app_ctx.config.deploy.max_replicas,
        "port": app_ctx.config.deploy.port,
        "gpu_type": app_ctx.config.deploy.gpu_type,
        "gpu_count": app_ctx.config.deploy.gpu_count,
        "cpu": app_ctx.config.deploy.cpu,
        "memory": app_ctx.config.deploy.memory,
        "autoscaling": app_ctx.config.deploy.autoscaling,
    }

    if app_ctx.config.deploy.health_check_path:
        deploy_data["health_check_path"] = app_ctx.config.deploy.health_check_path
    if app_ctx.config.deploy.command:
        deploy_data["command"] = app_ctx.config.deploy.command

    # Add environment variables
    env_vars = [{"name": k, "value": v} for k, v in app_ctx.config.deploy.environment_variables.items()]
    env_vars.append({"name": "TOGETHER_API_BASE_URL", "value": API_URL})

    if "TOGETHER_API_KEY" not in app_ctx.state.secrets:
        set_secret(app_ctx, "TOGETHER_API_KEY", app_ctx.api_key, "Auth key for queue API")

    for name, secret_id in app_ctx.state.secrets.items():
        env_vars.append({"name": name, "value_from_secret": secret_id})

    deploy_data["environment_variables"] = env_vars

    # Add volumes
    volume_list = []
    for volume_name, mount_path in app_ctx.state.volumes.items():
        volume_list.append({"name": volume_name, "mount_path": mount_path})
    if volume_list:
        deploy_data["volumes"] = volume_list

    click.echo(json.dumps(deploy_data, indent=2))
    click.echo(f"Deploying model: {app_ctx.config.model_name}")

    # Try to update first, fallback to create if not found
    try:
        response = app_ctx.client.request(
            "PATCH",
            f"/v1/deployments/{app_ctx.config.model_name}",
            json=deploy_data,
        )
        click.echo("\N{CHECK MARK} Updated deployment")
    except httpx.HTTPStatusError as e:
        if e.response.status_code != 404:
            raise
        click.echo("\N{ROCKET} Creating new deployment")
        response = app_ctx.client.request("POST", "/v1/deployments", json=deploy_data)
        click.echo(f"\N{CHECK MARK} Deployed: {app_ctx.config.model_name}")

    return response


@jig.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Get deployment status"""
    app_ctx: AppContext = ctx.obj
    response = app_ctx.client.request("GET", f"/v1/deployments/{app_ctx.config.model_name}")
    click.echo(json.dumps(response, indent=2))


@jig.command()
@click.pass_context
@click.option("--follow", is_flag=True, help="Follow log output")
def logs(ctx: click.Context, follow: bool) -> None:
    """Get deployment logs"""
    app_ctx: AppContext = ctx.obj

    if not follow:
        response = app_ctx.client.request("GET", f"/v1/deployments/{app_ctx.config.model_name}/logs")
        if response and "lines" in response:
            for log_line in response["lines"]:
                click.echo(log_line)
        else:
            click.echo("No logs available")
        return

    url = f"https://{API_URL}/v1/deployments/{app_ctx.config.model_name}/logs?follow=true"
    try:
        with httpx.Client(headers={"Authorization": f"Bearer {app_ctx.api_key}"}, timeout=None) as http_client:
            with http_client.stream("GET", url) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if line:
                        for log_line in json.loads(line).get("lines", []):
                            click.echo(log_line)
    except KeyboardInterrupt:
        click.echo("\nStopped following logs")
    except Exception as e:
        click.echo(f"\nConnection ended: {e}")


@jig.command()
@click.pass_context
def destroy(ctx: click.Context) -> None:
    """Destroy deployment"""
    app_ctx: AppContext = ctx.obj
    app_ctx.client.request("DELETE", f"/v1/deployments/{app_ctx.config.model_name}")
    click.echo(f"\N{WASTEBASKET} Destroyed {app_ctx.config.model_name}")


@jig.command()
@click.pass_context
@click.option("--prompt", help="Job prompt")
@click.option("--payload", help="Job payload JSON")
@click.option("--watch", is_flag=True, help="Watch job status until completion")
def submit(ctx: click.Context, prompt: str | None, payload: str | None, watch: bool) -> None:
    """Submit a job to the deployment"""
    app_ctx: AppContext = ctx.obj

    if not prompt and not payload:
        raise click.ClickException("Either --prompt or --payload required")

    request_data = {
        "model": app_ctx.config.model_name,
        "payload": json.loads(payload) if payload else {"prompt": prompt},
        "priority": 1,
    }

    response = app_ctx.client.request("POST", "/v1/videos/generations", json=request_data)
    click.echo("\N{CHECK MARK} Submitted job")
    click.echo(json.dumps(response, indent=2))

    if watch and response and "requestId" in response:
        click.echo(f"\nWatching job {response['requestId']}...")
        watch_job_status(app_ctx, response["requestId"])


@jig.command("job-status")
@click.pass_context
@click.option("--request-id", required=True, help="Job request ID")
def job_status(ctx: click.Context, request_id: str) -> None:
    """Get status of a specific video job"""
    app_ctx: AppContext = ctx.obj
    response = app_ctx.client.request(
        "GET",
        f"/v1/videos/status?request_id={request_id}&model={app_ctx.config.model_name}",
    )
    click.echo(json.dumps(response, indent=2))


@jig.command("queue-status")
@click.pass_context
def queue_status(ctx: click.Context) -> None:
    """Get queue status for the deployment"""
    app_ctx: AppContext = ctx.obj
    response = app_ctx.client.request("GET", f"/internal/v1/queue/status?model={app_ctx.config.model_name}")
    click.echo(json.dumps(response, indent=2))


# Add subcommand groups
jig.add_command(secrets)
jig.add_command(volumes)
