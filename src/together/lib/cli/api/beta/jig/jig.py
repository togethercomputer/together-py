"""Main jig CLI commands (deploy, build, push, etc.)."""

from __future__ import annotations

import json
import time
import shlex
import shutil
import subprocess
from typing import Any, Optional
from pathlib import Path

import click
from rich.pretty import pprint

from together import Together
from together._exceptions import APIStatusError
from together.lib.cli.api._utils import handle_api_errors
from together.lib.cli.api.beta.jig._config import (
    DEBUG,
    API_URL,
    REGISTRY_URL,
    GENERATE_DOCKERFILE,
    State,
    Config,
)

# --- Helper Functions ---


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    """Run process with defaults"""
    return subprocess.run(cmd, capture_output=True, text=True, check=True)


def _generate_dockerfile(config: Config) -> str:
    """Generate Dockerfile from config"""
    apt = ""
    if config.image.system_packages:
        sys_pkgs = " ".join(config.image.system_packages or [])
        apt = f"""RUN --mount=type=cache,target=/var/cache/apt \\
  apt-get update && \\
  DEBIAN_FRONTEND=noninteractive \\
  apt-get install -y --no-install-recommends {sys_pkgs} && \\
  apt-get clean && rm -rf /var/lib/apt/lists/*
"""

    env = "\n".join(f"ENV {k}={v}" for k, v in config.image.environment.items())
    if env:
        env += "\n"

    run = "\n".join(f"RUN {cmd}" for cmd in config.image.run)
    if run:
        run += "\n"

    copy = "\n".join(f"COPY {file} {file}" for file in _get_files_to_copy(config))

    return f"""
# Build stage
FROM python:{config.image.python_version} AS builder

{apt}
# Grab UV to install python packages
COPY --from=ghcr.io/astral-sh/uv /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml .
RUN --mount=type=cache,target=/root/.cache/uv \\
    uv pip install --system --compile-bytecode .

# Final stage - slim image
FROM python:{config.image.python_version}-slim

{apt}
COPY --from=builder /usr/local/lib/python{config.image.python_version} /usr/local/lib/python{config.image.python_version}
COPY --from=builder /usr/local/bin /usr/local/bin

# Tini for proper signal handling
COPY --from=krallin/ubuntu-tini:latest /usr/local/bin/tini /tini
ENTRYPOINT ["/tini", "--"]

{env}
{run}
WORKDIR /app
{copy}
# this is temporarily needed if building from a monorepo
RUN --mount=type=bind,source=.,target=/src cp /src/.worker.p* worker.py 2>/dev/null || true
# this tag will set the X-Worker-Version header, used for rollout monitoring
RUN --mount=type=bind,source=.,target=/src git -C /src describe --tags --exact-match > VERSION

CMD {json.dumps(shlex.split(config.image.cmd))}"""


def _get_files_to_copy(config: Config) -> list[str]:
    """Get list of files to copy"""
    files = set(config.image.copy)
    if config.image.auto_include_git:
        try:
            if _run(["git", "status", "--porcelain"]).stdout.strip():
                raise RuntimeError("Git repository has uncommitted changes: auto_include_git not allowed.")
            git_files = _run(["git", "ls-files"]).stdout.strip().split("\n")
            files.update(f for f in git_files if f and f != ".")
        except subprocess.CalledProcessError:
            pass

    if "." in files:
        raise ValueError("Copying '.' is not allowed. Please enumerate specific files.")

    return sorted(files)


def _get_image(state: State, config: Config, tag: str = "latest") -> str:
    """Get full image name"""
    return f"{REGISTRY_URL}/{state.username}/{config.model_name}:{tag}"


def _get_image_with_digest(state: State, config: Config, tag: str = "latest") -> str:
    """Get full image name tagged with digest"""
    image_name = _get_image(state, config, tag)
    if tag != "latest":
        return image_name
    try:
        cmd = ["docker", "inspect", "--format={{json .RepoDigests}}", image_name]
        repo_digests = _run(cmd).stdout.strip()
        if repo_digests and repo_digests != "null":
            registry = image_name.rsplit("/", 2)[0]
            for digest in json.loads(repo_digests):
                if digest.startswith(registry):
                    return digest
    except subprocess.CalledProcessError as e:
        msg = e.stderr.strip() if e.stderr else "Docker command failed"
        raise RuntimeError(f"Failed to get digest for {image_name}: {msg}")
    raise RuntimeError(f"No registry digest found for {image_name}. Make sure the image was pushed to registry first.")


def _set_secret(client: Together, config: Config, state: State, name: str, value: str, description: str) -> None:
    """Set secret for the deployment"""
    deployment_secret_name = f"{config.model_name}-{name}"

    try:
        client.beta.jig.secrets.retrieve(deployment_secret_name)
        client.beta.jig.secrets.update(
            deployment_secret_name,
            name=deployment_secret_name,
            description=description,
            value=value,
        )
        click.echo(f"\N{CHECK MARK} Updated secret: '{name}'")
    except APIStatusError as e:
        if hasattr(e, "status_code") and e.status_code == 404:
            click.echo("\N{ROCKET} Creating new secret")
            client.beta.jig.secrets.create(
                name=deployment_secret_name,
                value=value,
                description=description,
            )
            click.echo(f"\N{CHECK MARK} Created secret: {name}")
        else:
            raise

    state.secrets[name] = deployment_secret_name
    state.save()


def _watch_job_status(client: Together, config: Config, request_id: str) -> None:
    """Watch job status until completion"""
    last_status = None
    while True:
        try:
            # Use raw client request since this endpoint may not be in SDK
            response = client._client.get(
                f"/videos/status",
                params={"request_id": request_id, "model": config.model_name},
            )
            response.raise_for_status()
            data = response.json()
            current_status = data.get("status", "")
            if current_status != last_status:
                pprint(data, indent_guides=False)
                last_status = current_status

            if current_status in ["done", "failed", "finished", "error"]:
                break

            time.sleep(1)

        except KeyboardInterrupt:
            click.echo(f"\nStopped watching {request_id}")
            break


def _ensure_username(client: Together, state: State) -> None:
    """Ensure username is set in state"""
    if not state.username:
        response = client._client.get("/user/proof-data")
        response.raise_for_status()
        data = response.json()
        state.username = data["projectId"].lower()
        state.save()


# --- CLI Commands ---


@click.command()
def init() -> None:
    """Initialize jig configuration"""
    if (pyproject := Path("pyproject.toml")).exists():
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
    click.echo("  Edit the configuration and run 'jig deploy'")


@click.command()
@click.pass_context
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Jig")
def dockerfile(ctx: click.Context, config_path: str | None) -> None:
    """Generate Dockerfile"""
    config = Config.find(config_path)
    if not GENERATE_DOCKERFILE:
        click.echo("Set GENERATE_DOCKERFILE=1 to enable dockerfile generation")
    else:
        with open(config.dockerfile, "w") as f:
            f.write(_generate_dockerfile(config))
        click.echo("\N{CHECK MARK} Generated Dockerfile")


@click.command()
@click.pass_context
@click.option("--tag", default="latest", help="Image tag")
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Jig")
def build(ctx: click.Context, tag: str, config_path: str | None) -> None:
    """Build container image"""
    client: Together = ctx.obj
    config = Config.find(config_path)
    state = State.load(config._path.parent)
    _ensure_username(client, state)

    image = _get_image(state, config, tag)

    if GENERATE_DOCKERFILE:
        dockerfile_path = Path(config.dockerfile)
        if (
            config._path
            and config._path.exists()
            and dockerfile_path.exists()
            and config._path.stat().st_mtime > dockerfile_path.stat().st_mtime
        ):
            msg = f"\N{INFORMATION SOURCE} {config._path} has changed, regenerating Dockerfile"
            click.echo(msg)
            ctx.invoke(dockerfile, config_path=config_path)

        if not dockerfile_path.exists():
            ctx.invoke(dockerfile, config_path=config_path)

    build_dir_worker_path = Path("./.sprocket.py")
    dst = Path(__file__).parent / "sprocket" / "sprocket.py"
    try:
        shutil.copy(dst, build_dir_worker_path)
    except FileNotFoundError:
        pass

    click.echo(f"Building {image}")
    cmd = ["docker", "build", "--platform", "linux/amd64", "-t", image, "."]
    if config.dockerfile != "Dockerfile":
        cmd.extend(["-f", config.dockerfile])
    if subprocess.run(cmd).returncode != 0:
        raise RuntimeError("Build failed")

    build_dir_worker_path.unlink(missing_ok=True)
    click.echo("\N{CHECK MARK} Built")


@click.command()
@click.pass_context
@click.option("--tag", default="latest", help="Image tag")
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Jig")
def push(ctx: click.Context, tag: str, config_path: str | None) -> None:
    """Push image to registry"""
    client: Together = ctx.obj
    config = Config.find(config_path)
    state = State.load(config._path.parent)
    _ensure_username(client, state)

    image = _get_image(state, config, tag)

    login_cmd = f"echo {client.api_key} | docker login {REGISTRY_URL} --username user --password-stdin"
    if subprocess.run(login_cmd, shell=True, capture_output=True).returncode != 0:
        raise RuntimeError("Registry login failed")

    click.echo(f"Pushing {image}")
    if subprocess.run(["docker", "push", image]).returncode != 0:
        raise RuntimeError("Push failed")
    click.echo("\N{CHECK MARK} Pushed")


@click.command()
@click.pass_context
@click.option("--tag", default="latest", help="Image tag")
@click.option("--build-only", is_flag=True, help="Build and push only")
@click.option("--image", "existing_image", default=None, help="Use existing image (skip build/push)")
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Jig")
def deploy(
    ctx: click.Context,
    tag: str,
    build_only: bool,
    existing_image: str | None,
    config_path: str | None,
) -> Optional[dict[str, Any]]:
    """Deploy model"""
    client: Together = ctx.obj
    config = Config.find(config_path)
    state = State.load(config._path.parent)
    _ensure_username(client, state)

    if existing_image:
        deployment_image = existing_image
    else:
        # Invoke build and push
        ctx.invoke(build, tag=tag, config_path=config_path)
        ctx.invoke(push, tag=tag, config_path=config_path)
        deployment_image = _get_image_with_digest(state, config, tag)

    if build_only:
        click.echo("\N{CHECK MARK} Build complete (--build-only)")
        return None

    deploy_data: dict[str, Any] = {
        "name": config.model_name,
        "description": config.deploy.description,
        "image": deployment_image,
        "min_replicas": config.deploy.min_replicas,
        "max_replicas": config.deploy.max_replicas,
        "port": config.deploy.port,
        "gpu_type": config.deploy.gpu_type,
        "gpu_count": config.deploy.gpu_count,
        "cpu": config.deploy.cpu,
        "memory": config.deploy.memory,
        "autoscaling": config.deploy.autoscaling,
    }

    if config.deploy.health_check_path:
        deploy_data["health_check_path"] = config.deploy.health_check_path
    if config.deploy.command:
        deploy_data["command"] = config.deploy.command

    env_vars = [{"name": k, "value": v} for k, v in config.deploy.environment_variables.items()]
    env_vars.append({"name": "TOGETHER_API_BASE_URL", "value": API_URL})

    if "TOGETHER_API_KEY" not in state.secrets:
        _set_secret(client, config, state, "TOGETHER_API_KEY", client.api_key, "Auth key for queue API")

    for name, secret_id in state.secrets.items():
        env_vars.append({"name": name, "value_from_secret": secret_id})

    deploy_data["environment_variables"] = env_vars

    volumes = []
    for volume_name, mount_path in state.volumes.items():
        volumes.append({"name": volume_name, "mount_path": mount_path})

    deploy_data["volumes"] = volumes

    if DEBUG:
        pprint(deploy_data, indent_guides=False)
    click.echo(f"Deploying model: {config.model_name}")

    try:
        response = client.beta.jig.update(config.model_name, **deploy_data)
        click.echo("\N{CHECK MARK} Updated deployment")
    except APIStatusError as e:
        if hasattr(e, "status_code") and e.status_code == 404:
            click.echo("\N{ROCKET} Creating new deployment")
            response = client.beta.jig.deploy(**deploy_data)
            click.echo(f"\N{CHECK MARK} Deployed: {config.model_name}")
        else:
            raise

    return response.model_dump() if hasattr(response, "model_dump") else response


@click.command()
@click.pass_context
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Jig")
def status(ctx: click.Context, config_path: str | None) -> None:
    """Get deployment status"""
    client: Together = ctx.obj
    config = Config.find(config_path)
    response = client.beta.jig.retrieve(config.model_name)
    pprint(response.model_dump() if hasattr(response, "model_dump") else response, indent_guides=False)


@click.command()
@click.pass_context
@click.option("--follow", is_flag=True, help="Follow log output")
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Jig")
def logs(ctx: click.Context, follow: bool, config_path: str | None) -> None:
    """Get deployment logs"""
    client: Together = ctx.obj
    config = Config.find(config_path)

    if not follow:
        response = client.beta.jig.retrieve_logs(config.model_name)
        if hasattr(response, "lines") and response.lines:
            for log_line in response.lines:
                click.echo(log_line)
        else:
            click.echo("No logs available")
        return

    # Stream logs
    url = f"https://{API_URL}/v1/deployments/{config.model_name}/logs?follow=true"
    try:
        resp = client._client.get(url, timeout=None)
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                for log_line in json.loads(line).get("lines", []):
                    click.echo(log_line)
    except KeyboardInterrupt:
        click.echo("\nStopped following logs")
    except Exception as e:
        click.echo(f"\nConnection ended: {e}")


@click.command()
@click.pass_context
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Jig")
def destroy(ctx: click.Context, config_path: str | None) -> None:
    """Destroy deployment"""
    client: Together = ctx.obj
    config = Config.find(config_path)
    client.beta.jig.destroy(config.model_name)
    click.echo(f"\N{WASTEBASKET} Destroyed {config.model_name}")


@click.command()
@click.pass_context
@click.option("--prompt", default=None, help="Job prompt")
@click.option("--payload", default=None, help="Job payload JSON")
@click.option("--watch", is_flag=True, help="Watch job status until completion")
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Jig")
def submit(
    ctx: click.Context,
    prompt: str | None,
    payload: str | None,
    watch: bool,
    config_path: str | None,
) -> None:
    """Submit a job to the deployment"""
    client: Together = ctx.obj
    config = Config.find(config_path)

    if not prompt and not payload:
        raise click.UsageError("Either --prompt or --payload required")

    request_data = {
        "model": config.model_name,
        "payload": json.loads(payload) if payload else {"prompt": prompt},
        "priority": 1,
    }

    # Use raw client since this endpoint may not be in SDK
    response = client._client.post("/videos/generations", json=request_data)
    response.raise_for_status()
    data = response.json()

    click.echo("\N{CHECK MARK} Submitted job")
    pprint(data, indent_guides=False)

    if watch and "requestId" in data:
        click.echo(f"\nWatching job {data['requestId']}...")
        _watch_job_status(client, config, data["requestId"])


@click.command()
@click.pass_context
@click.option("--request-id", required=True, help="Job request ID")
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Jig")
def job_status(ctx: click.Context, request_id: str, config_path: str | None) -> None:
    """Get status of a specific video job"""
    client: Together = ctx.obj
    config = Config.find(config_path)

    response = client._client.get(
        "/videos/status",
        params={"request_id": request_id, "model": config.model_name},
    )
    response.raise_for_status()
    pprint(response.json(), indent_guides=False)


@click.command()
@click.pass_context
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Jig")
def queue_status(ctx: click.Context, config_path: str | None) -> None:
    """Get queue status for the deployment"""
    client: Together = ctx.obj
    config = Config.find(config_path)

    response = client._client.get(
        "/internal/v1/queue/status",
        params={"model": config.model_name},
    )
    response.raise_for_status()
    pprint(response.json(), indent_guides=False)


@click.command("list")
@click.pass_context
@handle_api_errors("Jig")
def list_deployments(ctx: click.Context) -> None:
    """List all deployments"""
    client: Together = ctx.obj
    response = client.beta.jig.list()
    pprint(response.model_dump() if hasattr(response, "model_dump") else response, indent_guides=False)
