"""Main jig CLI commands (deploy, build, push, etc.)."""

from __future__ import annotations

import json
import time
import shlex
import shutil
import subprocess
from typing import Any, Optional
from pathlib import Path
from dataclasses import asdict
from urllib.parse import urlparse

import click

from together import Together
from together._exceptions import APIStatusError
from together.lib.cli.api._utils import handle_api_errors
from together.lib.cli.api.beta.jig._config import (
    DEBUG,
    WARMUP_DEST,
    WARMUP_ENV_NAME,
    State,
    Config,
)
from together.types.beta.jig.queue_submit_response import QueueSubmitResponse

# Managed dockerfile marker - if this is the first line, jig will regenerate the file
DOCKERFILE_MANAGED_MARKER = "# MANAGED BY JIG - Remove this line to prevent jig from overwriting this file"

# --- Helper Functions ---


def _get_api_base_url(client: Together) -> str:
    """Extract base URL (scheme://host) from client, stripping any path like /v1"""
    parsed = urlparse(str(client.base_url))
    return f"{parsed.scheme}://{parsed.netloc}"


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    """Run process with defaults"""
    return subprocess.run(cmd, capture_output=True, text=True, check=True)


def _generate_dockerfile(config: Config) -> str:
    """Generate Dockerfile from config"""
    apt = ""
    if config.image.system_packages:
        sys_pkgs = " ".join(config.image.system_packages or [])
        apt = f"""RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \\
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

    # Check if .git exists in current directory
    if Path(".git").exists():
        git_version_cmd = 'RUN --mount=type=bind,source=.git,target=/git git --git-dir /git describe --tags --exact-match > VERSION || echo "0.0.0-dev" > VERSION'
    else:
        git_version_cmd = 'RUN echo "0.0.0-dev" > VERSION'

    return f"""{DOCKERFILE_MANAGED_MARKER}

# Build stage
FROM python:{config.image.python_version} AS builder

{apt}
# Grab UV to install python packages
COPY --from=ghcr.io/astral-sh/uv /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml .
RUN --mount=type=cache,target=/root/.cache/uv \\
    uv pip install --system --compile-bytecode . && \\
    (python -c "import sprocket" 2>/dev/null || (echo "sprocket not found in pyproject.toml, installing from pypi.together.ai..." && uv pip install --system --extra-index-url https://pypi.together.ai/ sprocket))

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
ENV DEPLOYMENT_NAME={config.model_name}
# this tag will set the X-Worker-Version header, used for rollout monitoring
{git_version_cmd}

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


def _dockerfile(config: Config) -> bool:
    """Generate Dockerfile if appropriate.

    Returns True if Dockerfile was generated, False if skipped (user-managed file exists).

    Logic:
    - If no Dockerfile exists → generate and return True
    - If Dockerfile exists without our marker → skip and return False (user-managed)
    - If Dockerfile exists with marker but config is older → skip and return True (no-op)
    - If Dockerfile exists with marker and config is newer → regenerate and return True
    """
    dockerfile_path = Path(config.dockerfile)

    if dockerfile_path.exists():
        with open(dockerfile_path) as f:
            first_line = f.readline().strip()

        if first_line != DOCKERFILE_MANAGED_MARKER:
            return False

        # Skip regeneration if config hasn't changed
        if config._path and config._path.exists() and dockerfile_path.stat().st_mtime >= config._path.stat().st_mtime:
            return True

    with open(dockerfile_path, "w") as f:
        f.write(_generate_dockerfile(config))

    return True


def _get_image(state: State, config: Config, tag: str = "latest") -> str:
    """Get full image name"""
    return f"{state.registry_base_path}/{config.model_name}:{tag}"


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
                    return str(digest)
    except subprocess.CalledProcessError as e:
        msg = e.stderr.strip() if e.stderr else "Docker command failed"
        raise RuntimeError(f"Failed to get digest for {image_name}: {msg}") from e
    raise RuntimeError(f"No registry digest found for {image_name}. Make sure the image was pushed to registry first.")


def _set_secret(
    client: Together,
    config: Config,
    state: State,
    name: str,
    value: str,
    description: str,
) -> None:
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
            response = client.beta.jig.queue.retrieve(
                model=config.model_name,
                request_id=request_id,
            )
            current_status = response.status
            if current_status != last_status:
                click.echo(response.model_dump_json(indent=2))
                last_status = current_status

            if current_status in ["done", "failed", "finished", "error"]:
                break

            time.sleep(1)

        except KeyboardInterrupt:
            click.echo(f"\nStopped watching {request_id}")
            break


def _ensure_registry_base_path(client: Together, state: State) -> None:
    """Ensure registry base path is set in state"""
    if not state.registry_base_path:
        response = client._client.get("/image-repositories/base-path", headers=client.auth_headers)
        response.raise_for_status()
        data = response.json()
        base_path = data["base-path"]
        # Strip protocol prefix - Docker tags don't support URLs
        if base_path.startswith("https://"):
            base_path = base_path[8:]
        elif base_path.startswith("http://"):
            base_path = base_path[7:]
        state.registry_base_path = base_path
        state.save()


def _build_warm_image(base_image: str) -> None:
    """Run a warmup container to generate a cache, then rebuild with cache baked in.

    This runs the container with RUN_AND_EXIT=1 which triggers warmup_inputs in sprocket.
    The cache directory is mounted at /app/torch_cache and the user's code should set the
    appropriate env var (TORCHINDUCTOR_CACHE_DIR, TKCC_OUTPUT_DIR, etc.) to point there.
    """
    import os

    cache_dir = Path(".") / WARMUP_DEST
    # Clean any existing cache
    try:
        shutil.rmtree(cache_dir)
    except FileNotFoundError:
        pass
    cache_dir.mkdir(exist_ok=True)

    click.echo("\N{FIRE} Running warmup to generate compile cache...")

    # Run container with GPU and RUN_AND_EXIT=1
    # Mount current dir as /app so warmup_inputs can reference local weights
    # Mount cache dir for compile artifacts
    warmup_cmd = ["docker", "run", "--rm", "--gpus", "all", "-e", "RUN_AND_EXIT=1"]
    warmup_cmd.extend(["-e", f"{WARMUP_ENV_NAME}=/app/{WARMUP_DEST}"])
    warmup_cmd.extend(["-v", f"{Path.cwd().absolute()}:/app"])
    # if MODEL_PRELOAD_PATH is set, also mount that (e.g. ~/.cache/huggingface)
    if weights_path := os.getenv("MODEL_PRELOAD_PATH"):
        warmup_cmd.extend(["-v", f"{weights_path}:{weights_path}"])
        warmup_cmd.extend(["-e", f"MODEL_PRELOAD_PATH={weights_path}"])
    warmup_cmd.append(base_image)

    click.echo(f"Running: {' '.join(warmup_cmd)}")
    result = subprocess.run(warmup_cmd)
    if result.returncode != 0:
        raise RuntimeError(f"Warmup failed with code {result.returncode}")

    # Check cache was generated
    cache_files = list(cache_dir.rglob("*"))
    if not cache_files:
        raise RuntimeError("Warmup completed but no cache files were generated")

    click.echo(f"\N{CHECK MARK} Warmup complete, {len(cache_files)} cache files generated")

    # Generate cache dockerfile - copy cache to same location used during warmup
    cache_dockerfile = Path("Dockerfile.cache")
    dockerfile_content = f"""FROM {base_image}
COPY {cache_dir.name} /app/{WARMUP_DEST}
ENV {WARMUP_ENV_NAME}=/app/{WARMUP_DEST}"""
    cache_dockerfile.write_text(dockerfile_content)

    click.echo("\N{PACKAGE} Building final image with cache...")
    cmd = ["docker", "build", "--platform", "linux/amd64", "-t", base_image]
    cmd.extend(["-f", str(cache_dockerfile), "."])

    if subprocess.run(cmd).returncode != 0:
        cache_dockerfile.unlink(missing_ok=True)
        raise RuntimeError("Cache image build failed")
    cache_dockerfile.unlink(missing_ok=True)
    click.echo("\N{CHECK MARK} Final image with cache built")


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
dependencies = ["torch", "transformers", "sprocket"]

[[tool.uv.index]]
name = "together-pypi"
url = "https://pypi.together.ai/"

[tool.uv.sources]
sprocket = { index = "together-pypi" }

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
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Jig")
def dockerfile(config_path: str | None) -> None:
    """Generate Dockerfile"""
    config = Config.find(config_path)
    if _dockerfile(config):
        click.echo("\N{CHECK MARK} Generated Dockerfile")
    else:
        click.echo(
            f"ERROR: {config.dockerfile} exists and is not managed by jig. "
            f"Remove or rename the file to allow jig to manage dockerfile.",
            err=True,
        )


@click.command()
@click.pass_context
@click.option("--tag", default="latest", help="Image tag")
@click.option("--warmup", is_flag=True, help="Run warmup to build torch compile cache")
@click.option(
    "--docker-args",
    default=None,
    help="Extra args for docker build (or use DOCKER_BUILD_EXTRA_ARGS env)",
)
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Jig")
def build(
    ctx: click.Context,
    tag: str,
    warmup: bool,
    docker_args: str | None,
    config_path: str | None,
) -> None:
    """Build container image"""
    import os
    import shlex as shlex_module

    client: Together = ctx.obj
    config = Config.find(config_path)
    state = State.load(config._path.parent)
    _ensure_registry_base_path(client, state)

    image = _get_image(state, config, tag)

    if _dockerfile(config):
        click.echo("\N{CHECK MARK} Generated Dockerfile")
    else:
        click.echo(f"\N{INFORMATION SOURCE} Using existing {config.dockerfile} (not managed by jig)")

    click.echo(f"Building {image}")
    cmd = ["docker", "build", "--platform", "linux/amd64", "-t", image, "."]
    if config.dockerfile != "Dockerfile":
        cmd.extend(["-f", config.dockerfile])

    # Add extra docker args from flag or env
    extra_args = docker_args or os.getenv("DOCKER_BUILD_EXTRA_ARGS", "")
    if extra_args:
        cmd.extend(shlex_module.split(extra_args))
    if subprocess.run(cmd).returncode != 0:
        raise RuntimeError("Build failed")

    click.echo("\N{CHECK MARK} Built")

    if warmup:
        _build_warm_image(image)


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
    _ensure_registry_base_path(client, state)

    image = _get_image(state, config, tag)

    registry = state.registry_base_path.split("/")[0]
    login_cmd = f"echo {client.api_key} | docker login {registry} --username user --password-stdin"
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
@click.option("--warmup", is_flag=True, help="Run warmup to build torch compile cache")
@click.option(
    "--docker-args",
    default=None,
    help="Extra args for docker build (or use DOCKER_BUILD_EXTRA_ARGS env)",
)
@click.option(
    "--image",
    "existing_image",
    default=None,
    help="Use existing image (skip build/push)",
)
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Jig")
def deploy(
    ctx: click.Context,
    tag: str,
    build_only: bool,
    warmup: bool,
    docker_args: str | None,
    existing_image: str | None,
    config_path: str | None,
) -> Optional[dict[str, Any]]:
    """Deploy model"""
    client: Together = ctx.obj
    config = Config.find(config_path)
    state = State.load(config._path.parent)
    _ensure_registry_base_path(client, state)

    if existing_image:
        deployment_image = existing_image
    else:
        # Invoke build and push
        ctx.invoke(
            build,
            tag=tag,
            warmup=warmup,
            docker_args=docker_args,
            config_path=config_path,
        )
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
        "storage": config.deploy.storage,
        "autoscaling": config.deploy.autoscaling,
        "termination_grace_period_seconds": config.deploy.termination_grace_period_seconds,
        "volumes": [asdict(vm) for vm in config.deploy.volume_mounts],
    }

    if config.deploy.health_check_path:
        deploy_data["health_check_path"] = config.deploy.health_check_path
    if config.deploy.command:
        deploy_data["command"] = config.deploy.command

    env_vars = [{"name": k, "value": v} for k, v in config.deploy.environment_variables.items()]
    env_vars.append({"name": "TOGETHER_API_BASE_URL", "value": _get_api_base_url(client)})

    if "TOGETHER_API_KEY" not in state.secrets:
        _set_secret(
            client,
            config,
            state,
            "TOGETHER_API_KEY",
            client.api_key,
            "Auth key for queue API",
        )

    for name, secret_id in state.secrets.items():
        env_vars.append({"name": name, "value_from_secret": secret_id})

    deploy_data["environment_variables"] = env_vars

    if DEBUG:
        click.echo(json.dumps(deploy_data, indent=2))
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

    return response.model_dump()


@click.command()
@click.pass_context
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Jig")
def status(ctx: click.Context, config_path: str | None) -> None:
    """Get deployment status"""
    client: Together = ctx.obj
    config = Config.find(config_path)
    response = client.beta.jig.with_raw_response.retrieve(config.model_name)
    click.echo(json.dumps(response.json(), indent=2))


@click.command()
@click.pass_context
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Jig")
def endpoint(ctx: click.Context, config_path: str | None) -> None:
    """Get deployment endpoint URL"""
    client: Together = ctx.obj
    config = Config.find(config_path)
    click.echo(f"{_get_api_base_url(client)}/v1/deployment-request/{config.model_name}")


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

    # Stream logs using SDK streaming response
    try:
        with client.beta.jig.with_streaming_response.retrieve_logs(config.model_name) as streaming_response:
            for line in streaming_response.iter_lines():
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

    raw_response = client.beta.jig.queue.with_raw_response.submit(
        model=config.model_name,
        payload=json.loads(payload) if payload else {"prompt": prompt},
        priority=1,
    )

    # Getting raw response and parsing ourselves here due to Stainless limitation with
    # Pydantic aliases not handled correctly (both fields are present in the model)
    response = QueueSubmitResponse.model_validate_json(raw_response.read())

    click.echo("\N{CHECK MARK} Submitted job")
    click.echo(response.model_dump_json(indent=2))

    if watch and response.request_id:
        click.echo(f"\nWatching job {response.request_id}...")
        _watch_job_status(client, config, response.request_id)


@click.command()
@click.pass_context
@click.option("--request-id", required=True, help="Job request ID")
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Jig")
def job_status(ctx: click.Context, request_id: str, config_path: str | None) -> None:
    """Get status of a specific job"""
    client: Together = ctx.obj
    config = Config.find(config_path)

    response = client.beta.jig.queue.retrieve(
        model=config.model_name,
        request_id=request_id,
    )
    click.echo(response.model_dump_json(indent=2))


@click.command()
@click.pass_context
@click.option("--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Jig")
def queue_status(ctx: click.Context, config_path: str | None) -> None:
    """Get queue metrics for the deployment"""
    client: Together = ctx.obj
    config = Config.find(config_path)

    response = client.beta.jig.queue.with_raw_response.metrics(model=config.model_name)
    click.echo(json.dumps(response.json(), indent=2))


@click.command("list")
@click.pass_context
@handle_api_errors("Jig")
def list_deployments(ctx: click.Context) -> None:
    """List all deployments"""
    client: Together = ctx.obj
    response = client.beta.jig.with_raw_response.list()
    click.echo(json.dumps(response.json(), indent=2))
