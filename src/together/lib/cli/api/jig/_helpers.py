"""Helper functions for jig deployment tool."""

from __future__ import annotations

import asyncio
import json
import os
import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Coroutine

import httpx

if TYPE_CHECKING:
    from ._client import APIClient
    from ._config import Config
    from ._state import State

# Upload configuration
UPLOAD_CONCURRENCY_LIMIT = int(os.getenv("TOGETHER_UPLOAD_CONCURRENCY", "15"))
MULTIPART_CHUNK_SIZE_MB = int(os.getenv("TOGETHER_MULTIPART_CHUNK_SIZE_MB", "20"))
MULTIPART_THRESHOLD_MB = int(os.getenv("TOGETHER_MULTIPART_THRESHOLD_MB", "100"))
MAX_UPLOAD_RETRIES = 3

GENERATE_DOCKERFILE = os.getenv("GENERATE_DOCKERFILE", "0") != "0"


@dataclass
class AppContext:
    """Shared application context passed to commands."""

    config: Config
    state: State
    client: APIClient
    api_key: str


def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    """Run process with defaults."""
    return subprocess.run(cmd, capture_output=True, text=True, check=True)


def get_image(app_ctx: AppContext, tag: str = "latest") -> str:
    """Get full image name."""
    from ._client import REGISTRY_URL

    return f"{REGISTRY_URL}/{app_ctx.state.username}/{app_ctx.config.model_name}:{tag}"


def get_image_with_digest(app_ctx: AppContext, tag: str = "latest") -> str:
    """Get full image name tagged with digest."""
    image_name = get_image(app_ctx, tag)
    if tag != "latest":
        return image_name

    try:
        cmd = ["docker", "inspect", "--format={{json .RepoDigests}}", image_name]
        repo_digests = run_cmd(cmd).stdout.strip()
        if repo_digests and repo_digests != "null":
            registry = image_name.rsplit("/", 2)[0]
            for digest in json.loads(repo_digests):
                if digest.startswith(registry):
                    return str(digest)
    except subprocess.CalledProcessError as e:
        msg = e.stderr.strip() if e.stderr else "Docker command failed"
        raise RuntimeError(f"Failed to get digest for {image_name}: {msg}") from e

    raise RuntimeError(f"No registry digest found for {image_name}. Make sure the image was pushed to registry first.")


def get_files_to_copy(config: Config) -> list[str]:
    """Get list of files to copy for Dockerfile."""
    files = set(config.image.copy)

    if config.image.auto_include_git:
        try:
            if run_cmd(["git", "status", "--porcelain"]).stdout.strip():
                raise RuntimeError("Git repository has uncommitted changes: auto_include_git not allowed.")
            git_files = run_cmd(["git", "ls-files"]).stdout.strip().split("\n")
            files.update(f for f in git_files if f and f != ".")
        except subprocess.CalledProcessError:
            pass  # Not a git repo or git not available

    if "." in files:
        raise ValueError("Copying '.' is not allowed. Please enumerate specific files.")

    return sorted(files)


def generate_dockerfile(config: Config) -> str:
    """Generate Dockerfile from config."""
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

    copy = "\n".join(f"COPY {file} {file}" for file in get_files_to_copy(config))

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


def do_dockerfile(config: Config) -> None:
    """Generate Dockerfile helper."""
    if not GENERATE_DOCKERFILE:
        print("Set GENERATE_DOCKERFILE=1 to enable dockerfile generation")
    else:
        with open(config.dockerfile, "w") as f:
            f.write(generate_dockerfile(config))
        print("\N{CHECK MARK} Generated Dockerfile")


def set_secret(app_ctx: AppContext, name: str, value: str, description: str) -> None:
    """Set secret for the deployment."""
    deployment_secret_name = f"{app_ctx.config.model_name}-{name}"
    secret_data = {
        "name": deployment_secret_name,
        "description": description,
        "value": value,
    }

    try:
        app_ctx.client.request("GET", f"/v1/secrets/{deployment_secret_name}")
        app_ctx.client.request("PATCH", f"/v1/secrets/{deployment_secret_name}", json=secret_data)
        print(f"\N{CHECK MARK} Updated secret: '{name}'")
    except httpx.HTTPStatusError as e:
        if e.response.status_code != 404:
            raise
        print("\N{ROCKET} Creating new secret")
        app_ctx.client.request("POST", "/v1/secrets", json=secret_data)
        print(f"\N{CHECK MARK} Created secret: {name}")

    app_ctx.state.secrets[name] = deployment_secret_name
    app_ctx.state.save()


def watch_job_status(app_ctx: AppContext, request_id: str) -> None:
    """Watch job status until completion."""
    last_status = None
    while True:
        try:
            response = app_ctx.client.request(
                "GET",
                f"/v1/videos/status?request_id={request_id}&model={app_ctx.config.model_name}",
            )
            current_status = (response or {}).get("status", "")
            if current_status != last_status:
                print(json.dumps(response, indent=2))
                last_status = current_status

            if current_status in ["done", "failed", "finished", "error"]:
                break

            time.sleep(1)

        except KeyboardInterrupt:
            print(f"\nStopped watching {request_id}")
            break


# --- Volume Upload Helpers ---


async def create_volume(app_ctx: AppContext, name: str, source: str) -> None:
    """Create a volume and upload files."""
    source_path = Path(source)
    if not source_path.exists():
        raise ValueError(f"Source path does not exist: {source}")
    if not source_path.is_dir():
        raise ValueError(f"Source path must be a directory: {source}")

    source_prefix = f"{name}/{source_path.name}"

    volume_data = {
        "name": name,
        "type": "readOnly",
        "content": {
            "type": "files",
            "source_prefix": source_prefix,
        },
    }

    print(f"\N{ROCKET} Creating volume '{name}' with source prefix '{source_prefix}'")
    try:
        volume_response = app_ctx.client.request("POST", "/v1/storage/volumes", json=volume_data)
        if volume_response is None:
            raise RuntimeError("Empty response from volume creation")
        print(f"\N{CHECK MARK} Volume created: {volume_response['id']}")
    except Exception as e:
        raise RuntimeError(f"Failed to create volume: {e}") from e

    try:
        await upload_files(app_ctx, source_path, volume_name=name)
    except Exception as e:
        print(f"\N{CROSS MARK} Upload failed: {e}")
        print(f"\N{WASTEBASKET} Cleaning up volume '{name}'")
        try:
            app_ctx.client.request("DELETE", f"/v1/storage/volumes/{name}")
        except Exception as cleanup_error:
            print(f"\N{WARNING SIGN} Failed to delete volume: {cleanup_error}")
        raise


async def update_volume(app_ctx: AppContext, name: str, source: str) -> None:
    """Update a volume and re-upload files."""
    source_path = Path(source)
    if not source_path.exists():
        raise ValueError(f"Source path does not exist: {source}")
    if not source_path.is_dir():
        raise ValueError(f"Source path must be a directory: {source}")

    try:
        app_ctx.client.request("GET", f"/v1/storage/volumes/{name}")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise ValueError(f"Volume '{name}' does not exist") from e
        raise

    source_prefix = f"{name}/{source_path.name}"

    print(f"\N{INFORMATION SOURCE} Uploading files for volume '{name}'")
    await upload_files(app_ctx, source_path, volume_name=name)

    volume_data = {
        "content": {
            "type": "files",
            "source_prefix": source_prefix,
        },
    }

    print(f"\N{INFORMATION SOURCE} Updating volume '{name}' with source prefix '{source_prefix}'")
    app_ctx.client.request("PATCH", f"/v1/storage/volumes/{name}", json=volume_data)
    print("\N{CHECK MARK} Volume updated successfully")


async def upload_files(app_ctx: AppContext, source_path: Path, volume_name: str) -> None:
    """Upload all files from source directory with progress tracking."""
    chunk_size = MULTIPART_CHUNK_SIZE_MB * 1024 * 1024
    multipart_threshold = MULTIPART_THRESHOLD_MB * 1024 * 1024
    source_prefix = f"{volume_name}/{source_path.name}"

    files_to_upload: list[tuple[Path, str, int]] = []
    for file_path in source_path.rglob("*"):
        if file_path.is_file():
            rel_path = file_path.relative_to(source_path)
            remote_path = f"{source_prefix}/{rel_path.as_posix()}"
            file_size = file_path.stat().st_size
            files_to_upload.append((file_path, remote_path, file_size))

    if not files_to_upload:
        raise ValueError(f"No files found in {source_path}")

    files_to_upload.sort(key=lambda x: x[2], reverse=True)

    total_parts = 0
    for _, _, file_size in files_to_upload:
        if file_size >= multipart_threshold:
            parts_count = (file_size + chunk_size - 1) // chunk_size
            total_parts += parts_count
        else:
            total_parts += 1

    completed_parts = 0
    completed_files = 0
    total_bytes = sum(size for _, _, size in files_to_upload)
    total_files = len(files_to_upload)
    start_time = time.time()
    progress_state: dict[str, Any] = {
        "current_file": "",
        "completed": 0,
        "completed_files": 0,
        "total": total_parts,
        "uploaded_bytes": 0,
        "elapsed": 0,
        "spinner_idx": 0,
    }
    spinner_chars = "|/-\\"
    progress_lock = asyncio.Lock()

    def format_filename(filename: str, max_len: int = 100) -> str:
        if len(filename) <= max_len:
            return filename
        return "..." + filename[-(max_len - 3) :]

    def update_progress() -> None:
        progress_state["spinner_idx"] = (progress_state["spinner_idx"] + 1) % len(spinner_chars)
        spinner = spinner_chars[progress_state["spinner_idx"]]
        percent = int(progress_state["completed"] * 100 / progress_state["total"]) if progress_state["total"] > 0 else 0

        display_file = format_filename(progress_state["current_file"])
        elapsed = progress_state["elapsed"]

        uploaded_mb = progress_state["uploaded_bytes"] / (1024 * 1024)
        total_mb = total_bytes / (1024 * 1024)
        size_str = f"({uploaded_mb:.1f}MB/{total_mb:.1f}MB)"

        if elapsed > 0.5 and progress_state["uploaded_bytes"] > 0:
            speed_bps = progress_state["uploaded_bytes"] / elapsed
            if speed_bps > 1024 * 1024:
                speed_str = f"{speed_bps / (1024 * 1024):.1f} MB/s"
            else:
                speed_str = f"{speed_bps / 1024:.1f} KB/s"
            msg = f"\r{spinner} {percent}% - {speed_str} - {display_file} {size_str} ({progress_state['completed_files']}/{total_files} files)"
        else:
            msg = f"\r{spinner} {percent}% - {display_file} {size_str} ({progress_state['completed_files']}/{total_files} files)"

        print(f"\r{msg}\033[K", end="", flush=True)

    async def increment_progress(bytes_count: int, filename: str = "", file_complete: bool = False) -> None:
        nonlocal completed_parts, completed_files
        async with progress_lock:
            if bytes_count > 0:
                completed_parts += 1
                progress_state["completed"] = completed_parts
                progress_state["uploaded_bytes"] += bytes_count
                progress_state["elapsed"] = time.time() - start_time
            if file_complete:
                completed_files += 1
                progress_state["completed_files"] = completed_files
            if filename:
                progress_state["current_file"] = filename
            update_progress()

    semaphore = asyncio.Semaphore(UPLOAD_CONCURRENCY_LIMIT)
    spinner_running = True

    async def spinner_updater() -> None:
        while spinner_running:
            async with progress_lock:
                update_progress()
            await asyncio.sleep(0.1)

    async def upload_file_with_retry(file_path: Path, remote_path: str, file_size: int) -> None:
        for attempt in range(MAX_UPLOAD_RETRIES):
            attempt_parts = 0
            attempt_bytes = 0

            async def track_progress(bytes_count: int, filename: str = "", file_complete: bool = False) -> None:
                nonlocal attempt_parts, attempt_bytes
                if bytes_count > 0:
                    attempt_parts += 1
                    attempt_bytes += bytes_count
                await increment_progress(bytes_count, filename, file_complete)

            try:
                if file_size >= multipart_threshold:
                    await upload_file_multipart(
                        app_ctx,
                        file_path,
                        remote_path,
                        file_size,
                        semaphore,
                        track_progress,
                        chunk_size,
                    )
                else:
                    await upload_file_simple(
                        app_ctx,
                        file_path,
                        remote_path,
                        file_size,
                        semaphore,
                        track_progress,
                    )
                return
            except Exception as e:
                async with progress_lock:
                    nonlocal completed_parts
                    completed_parts -= attempt_parts
                    progress_state["completed"] = completed_parts
                    progress_state["uploaded_bytes"] -= attempt_bytes
                if attempt == MAX_UPLOAD_RETRIES - 1:
                    raise RuntimeError(
                        f"Failed to upload {remote_path} after {MAX_UPLOAD_RETRIES} attempts: {e}"
                    ) from e
                await asyncio.sleep(1 * (attempt + 1))

    spinner_task = asyncio.create_task(spinner_updater())
    try:
        tasks = [upload_file_with_retry(fp, rp, fs) for fp, rp, fs in files_to_upload]
        await asyncio.gather(*tasks)
    finally:
        spinner_running = False
        await spinner_task

    elapsed_time = time.time() - start_time
    print(f"\n\N{CHECK MARK} Upload completed in {elapsed_time:.1f} seconds")


ProgressCallback = Callable[[int, str, bool], Coroutine[Any, Any, None]]


async def upload_file_simple(
    app_ctx: AppContext,
    file_path: Path,
    remote_path: str,
    file_size: int,
    semaphore: asyncio.Semaphore,
    on_complete: ProgressCallback,
) -> None:
    """Upload a single file using simple upload."""
    async with semaphore:
        response = app_ctx.client.request("POST", "/v1/storage/upload-request", json={"filename": remote_path})
        if response is None:
            raise RuntimeError("Empty response from upload request")

        upload_url = response["upload_url"]["url"]
        method = response["upload_url"]["method"]
        headers = response["upload_url"].get("headers", {})

        with open(file_path, "rb") as f:
            file_data = f.read()

        async with httpx.AsyncClient(timeout=300.0) as http_client:
            try:
                resp = await http_client.request(method, upload_url, content=file_data, headers=headers)
                resp.raise_for_status()
            except Exception as e:
                raise RuntimeError(f"Failed to upload {remote_path}: {e}") from e

        await on_complete(max(file_size, 1), remote_path, True)


async def upload_file_multipart(
    app_ctx: AppContext,
    file_path: Path,
    remote_path: str,
    file_size: int,
    semaphore: asyncio.Semaphore,
    on_complete: ProgressCallback,
    chunk_size: int,
) -> None:
    """Upload a file using multipart upload."""
    parts_count = (file_size + chunk_size - 1) // chunk_size

    response = app_ctx.client.request(
        "POST",
        "/v1/storage/multipart/init",
        json={"filename": remote_path, "parts_count": parts_count},
    )
    if response is None:
        raise RuntimeError("Empty response from multipart init")

    upload_id = response["upload_id"]
    part_urls = response["part_upload_urls"]

    try:
        completed_parts = await upload_parts(file_path, part_urls, chunk_size, semaphore, on_complete)

        app_ctx.client.request(
            "POST",
            "/v1/storage/multipart/complete",
            json={
                "filename": remote_path,
                "upload_id": upload_id,
                "parts": completed_parts,
            },
        )

        await on_complete(0, remote_path, True)
    except Exception:
        try:
            app_ctx.client.request(
                "POST",
                "/v1/storage/multipart/abort",
                json={"filename": remote_path, "upload_id": upload_id},
            )
        except Exception:
            pass
        raise


async def upload_parts(
    file_path: Path,
    part_urls: list[dict[str, Any]],
    chunk_size: int,
    semaphore: asyncio.Semaphore,
    on_complete: ProgressCallback,
) -> list[dict[str, Any]]:
    """Upload file parts concurrently."""
    async with httpx.AsyncClient(timeout=300.0) as http_client:

        async def upload_part(part_info: dict[str, Any]) -> dict[str, Any]:
            async with semaphore:
                part_number = part_info["part_number"]
                url = part_info["url"]
                method = part_info["method"]
                headers = part_info.get("headers", {})

                offset = (part_number - 1) * chunk_size

                with open(file_path, "rb") as f:
                    f.seek(offset)
                    data = f.read(chunk_size)

                part_size = len(data)

                for attempt in range(MAX_UPLOAD_RETRIES):
                    try:
                        response = await http_client.request(method, url, content=data, headers=headers)
                        response.raise_for_status()
                        etag = response.headers.get("ETag", "").strip('"')
                        await on_complete(
                            part_size,
                            f"{file_path.name} (part {part_number}/{len(part_urls)})",
                            False,
                        )
                        return {"part_number": part_number, "etag": etag}
                    except Exception as e:
                        if attempt == MAX_UPLOAD_RETRIES - 1:
                            raise RuntimeError(f"Failed to upload part {part_number}: {e}") from e
                        await asyncio.sleep(1 * (attempt + 1))
                raise RuntimeError(f"Failed to upload part {part_number}")

        tasks = [upload_part(part_info) for part_info in part_urls]
        completed_parts = await asyncio.gather(*tasks)
        return sorted(completed_parts, key=lambda x: x["part_number"])
