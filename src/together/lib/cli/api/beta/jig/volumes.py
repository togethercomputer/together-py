"""Volume management CLI commands for jig."""

from __future__ import annotations

import json
import time
import asyncio
import itertools
from typing import Any
from pathlib import Path

import click
import httpx

from together import Together
from together._exceptions import APIStatusError
from together.lib.cli.api._utils import handle_api_errors
from together.lib.cli.api.beta.jig._config import (
    DEBUG,
    MAX_UPLOAD_RETRIES,
    MULTIPART_THRESHOLD_MB,
    MULTIPART_CHUNK_SIZE_MB,
    UPLOAD_CONCURRENCY_LIMIT,
)


@click.group()
@click.pass_context
def volumes(ctx: click.Context) -> None:
    """Manage volumes"""
    pass


# --- File upload ---


def format_filename(filename: str, max_len: int = 100) -> str:
    if len(filename) <= max_len:
        return filename
    return "..." + filename[-(max_len - 3) :]


class Uploader:
    """Helper to handle file upload"""

    chunk_size = MULTIPART_CHUNK_SIZE_MB * 1024 * 1024
    multipart_threshold = MULTIPART_THRESHOLD_MB * 1024 * 1024
    spinner_chars = "|/-\\"

    def __init__(self, client: Together) -> None:
        self.client = client
        # progress
        self.start_time = time.time()
        self.completed_files = 0
        self.uploaded_bytes = 0
        self.current_file = ""
        self.total_bytes = 0
        self.total_files = 0
        # cycle through spinner chars forever
        self.spinner_running = True
        self.spinner_iter = itertools.cycle("|/-\\")
        # these will be set in upload_files when event loop is running
        self.semaphore: asyncio.Semaphore
        self.progress_lock: asyncio.Lock
        self.http_client: httpx.AsyncClient

    def update_progress(self) -> None:
        spinner = next(self.spinner_iter)

        bytes_denominator = self.total_bytes or float("inf")
        percent = int(100 * self.uploaded_bytes / bytes_denominator)

        display_file = format_filename(self.current_file)

        uploaded_mb = self.uploaded_bytes / (1024 * 1024)
        total_mb = self.total_bytes / (1024 * 1024)
        size_str = f"({uploaded_mb:.1f}MB/{total_mb:.1f}MB)"

        elapsed = time.time() - self.start_time
        speed_str = ""
        if elapsed > 0.5 and self.uploaded_bytes > 0:
            speed_kbps = self.uploaded_bytes / elapsed / 1024
            speed_str = f"{speed_kbps:.1f} KB/s - "
            if speed_kbps > 1024:
                speed_str = f"{(speed_kbps / 1024):.1f} MB/s - "

        msg = f"\r{spinner} {percent}% - {speed_str}{display_file} {size_str} ({self.completed_files}/{self.total_files} files)"

        # \r moves cursor to start of line, \033[K clears from cursor to end of line
        print(f"\r{msg}\033[K", end="", flush=True)  # noqa: T201

    async def increment_progress(self, bytes_count: int, filename: str = "", file_complete: bool = False) -> None:
        async with self.progress_lock:
            if bytes_count > 0:
                self.uploaded_bytes += bytes_count
            if DEBUG:
                click.echo(f"\nDEBUG: bytes_count={bytes_count}, total={self.uploaded_bytes}")
            if file_complete:
                self.completed_files += 1
            if filename:
                self.current_file = filename
            self.update_progress()

    async def spinner_updater(self) -> None:
        while self.spinner_running:
            async with self.progress_lock:
                self.update_progress()
            await asyncio.sleep(0.1)

    async def upload_files(self, source_path: Path, volume_name: str) -> None:
        """Upload all files from source directory with progress tracking"""
        # these require a running event loop
        self.semaphore = asyncio.Semaphore(UPLOAD_CONCURRENCY_LIMIT)
        self.progress_lock = asyncio.Lock()

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

        self.total_bytes = sum(size for _, _, size in files_to_upload)
        self.total_files = len(files_to_upload)
        spinner_task = asyncio.create_task(self.spinner_updater())
        async with httpx.AsyncClient(timeout=300.0) as self.http_client:
            try:
                tasks = [self.upload_file_with_retry(fp, rp, fs) for fp, rp, fs in files_to_upload]
                await asyncio.gather(*tasks)
            finally:
                self.spinner_running = False
                await spinner_task

        elapsed_time = time.time() - self.start_time
        click.echo(f"\n\N{CHECK MARK} Upload completed in {elapsed_time:.1f} seconds")

    async def upload_file_with_retry(self, file_path: Path, remote_path: str, file_size: int) -> None:
        for attempt in range(MAX_UPLOAD_RETRIES):
            # Snapshot progress before attempt
            async with self.progress_lock:
                snapshot_bytes = self.uploaded_bytes

            try:
                if file_size >= self.multipart_threshold:
                    await self._upload_file_multipart(file_path, remote_path, file_size)
                else:
                    await self._upload_file_simple(file_path, remote_path, file_size)
                return
            except Exception as e:
                # Rollback to snapshot on failure
                async with self.progress_lock:
                    self.uploaded_bytes = snapshot_bytes
                if attempt == MAX_UPLOAD_RETRIES - 1:
                    raise RuntimeError(
                        f"Failed to upload {remote_path} after {MAX_UPLOAD_RETRIES} attempts: {e}"
                    ) from e
                await asyncio.sleep(1 * (attempt + 1))

    async def _upload_file_simple(
        self,
        file_path: Path,
        remote_path: str,
        file_size: int,
    ) -> None:
        """Upload a single file using simple upload"""
        async with self.semaphore:
            response = self.client._client.post(
                "/storage/upload-request",
                json={"filename": remote_path},
                headers=self.client.auth_headers,
            )
            response.raise_for_status()
            upload_data = response.json()

            upload_url = upload_data["upload_url"]["url"]
            method = upload_data["upload_url"]["method"]
            headers = upload_data["upload_url"].get("headers", {})

            file_data = await asyncio.to_thread(Path(file_path).read_bytes)

            try:
                resp = await self.http_client.request(method, upload_url, content=file_data, headers=headers)
                resp.raise_for_status()
            except Exception as e:
                raise RuntimeError(f"Failed to upload {remote_path}: {e}") from e

            await self.increment_progress(max(file_size, 1), remote_path, file_complete=True)

    async def _upload_file_multipart(
        self,
        file_path: Path,
        remote_path: str,
        file_size: int,
    ) -> None:
        """Upload a file using multipart upload"""
        parts_count = (file_size + self.chunk_size - 1) // self.chunk_size

        response = self.client._client.post(
            "/storage/multipart/init",
            json={"filename": remote_path, "parts_count": parts_count},
            headers=self.client.auth_headers,
        )
        response.raise_for_status()
        init_data = response.json()

        upload_id = init_data["upload_id"]
        part_urls = init_data["part_upload_urls"]

        try:
            completed_parts = await self._upload_parts(file_path, part_urls)

            self.client._client.post(
                "/storage/multipart/complete",
                json={
                    "filename": remote_path,
                    "upload_id": upload_id,
                    "parts": completed_parts,
                },
                headers=self.client.auth_headers,
            )

            await self.increment_progress(0, remote_path, file_complete=True)
        except Exception:
            try:
                self.client._client.post(
                    "/storage/multipart/abort",
                    json={"filename": remote_path, "upload_id": upload_id},
                    headers=self.client.auth_headers,
                )
            except Exception as e:
                click.echo(f"Failed to abort multipart upload request: {repr(e)}")
            raise

    async def _upload_parts(
        self,
        file_path: Path,
        part_urls: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Upload file parts concurrently"""

        async def upload_part(part_info: dict[str, Any], data: bytes) -> dict[str, Any]:
            err = None
            async with self.semaphore:
                part_number = part_info["part_number"]
                url = part_info["url"]
                method = part_info["method"]
                headers = part_info.get("headers", {})

                part_size = len(data)

                for attempt in range(MAX_UPLOAD_RETRIES):
                    try:
                        response = await self.http_client.request(method, url, content=data, headers=headers)
                        response.raise_for_status()
                        etag = response.headers.get("ETag", "").strip('"')
                        await self.increment_progress(
                            part_size,
                            f"{file_path.name} (part {part_number}/{len(part_urls)})",
                        )
                        return {"part_number": part_number, "etag": etag}
                    except Exception as e:
                        err = e
                        if attempt < MAX_UPLOAD_RETRIES - 1:
                            await asyncio.sleep(1 * (attempt + 1))
                raise RuntimeError(f"Failed to upload part {part_number}: {err}")

        with open(file_path, "rb") as f:
            tasks = [
                asyncio.create_task(
                    upload_part(
                        part_info=part_info,
                        # read file sequentially while uploads proceed
                        data=await asyncio.to_thread(f.read, self.chunk_size),
                    )
                )
                for part_info in part_urls
            ]

        completed_parts = await asyncio.gather(*tasks)
        return sorted(completed_parts, key=lambda x: x["part_number"])


async def _create_volume(client: Together, name: str, source: str) -> None:
    """Create a volume and upload files"""
    source_path = Path(source)
    if not source_path.exists():
        raise ValueError(f"Source path does not exist: {source}")
    if not source_path.is_dir():
        raise ValueError(f"Source path must be a directory: {source}")

    source_prefix = f"{name}/{source_path.name}"

    click.echo(f"\N{ROCKET} Creating volume '{name}' with source prefix '{source_prefix}'")
    try:
        volume_response = client.beta.jig.volumes.create(
            name=name,
            type="readOnly",
            content={"type": "files", "source_prefix": source_prefix},
        )
        click.echo(f"\N{CHECK MARK} Volume created: {volume_response.id}")
    except Exception as e:
        raise RuntimeError(f"Failed to create volume: {e}") from e

    try:
        await Uploader(client).upload_files(source_path, volume_name=name)
    except Exception as e:
        click.echo(f"\N{CROSS MARK} Upload failed: {e}")
        click.echo(f"\N{WASTEBASKET} Cleaning up volume '{name}'")
        try:
            client.beta.jig.volumes.delete(name)
        except Exception as cleanup_error:
            click.echo(f"\N{WARNING SIGN} Failed to delete volume: {cleanup_error}")
        raise


async def _update_volume(client: Together, name: str, source: str) -> None:
    """Update a volume and re-upload files"""
    source_path = Path(source)
    if not source_path.exists():
        raise ValueError(f"Source path does not exist: {source}")
    if not source_path.is_dir():
        raise ValueError(f"Source path must be a directory: {source}")

    try:
        client.beta.jig.volumes.retrieve(name)
    except APIStatusError as e:
        if hasattr(e, "status_code") and e.status_code == 404:
            raise ValueError(f"Volume '{name}' does not exist") from e
        raise

    source_prefix = f"{name}/{source_path.name}"

    click.echo(f"\N{INFORMATION SOURCE} Uploading files for volume '{name}'")
    await Uploader(client).upload_files(source_path, volume_name=name)

    click.echo(f"\N{INFORMATION SOURCE} Updating volume '{name}' with source prefix '{source_prefix}'")
    client.beta.jig.volumes.update(
        name,
        content={"type": "files", "source_prefix": source_prefix},
    )
    click.echo("\N{CHECK MARK} Volume updated successfully")


# --- CLI Commands ---


@volumes.command("create")
@click.pass_context
@click.option("--name", required=True, help="Volume name")
@click.option("--source", required=True, help="Source directory path")
@handle_api_errors("Volumes")
def volumes_create(
    ctx: click.Context,
    name: str,
    source: str,
) -> None:
    """Create a volume and upload files"""
    client: Together = ctx.obj
    asyncio.run(_create_volume(client, name, source))


@volumes.command("update")
@click.pass_context
@click.option("--name", required=True, help="Volume name")
@click.option("--source", required=True, help="New source directory path")
@handle_api_errors("Volumes")
def volumes_update(
    ctx: click.Context,
    name: str,
    source: str,
) -> None:
    """Update a volume and re-upload files"""
    client: Together = ctx.obj
    asyncio.run(_update_volume(client, name, source))


@volumes.command("delete")
@click.pass_context
@click.option("--name", required=True, help="Volume name")
@handle_api_errors("Volumes")
def volumes_delete(
    ctx: click.Context,
    name: str,
) -> None:
    """Delete a volume"""
    client: Together = ctx.obj

    try:
        client.beta.jig.volumes.delete(name)
        click.echo(f"\N{CHECK MARK} Deleted volume '{name}'")
    except APIStatusError as e:
        if hasattr(e, "status_code") and e.status_code == 404:
            click.echo(f"\N{CROSS MARK} Volume '{name}' not found")
            return
        raise


@volumes.command("describe")
@click.pass_context
@click.option("--name", required=True, help="Volume name")
@handle_api_errors("Volumes")
def volumes_describe(
    ctx: click.Context,
    name: str,
) -> None:
    """Describe a volume"""
    client: Together = ctx.obj

    try:
        response = client.beta.jig.volumes.with_raw_response.retrieve(name)
        click.echo(json.dumps(response.json(), indent=2))
    except APIStatusError as e:
        if hasattr(e, "status_code") and e.status_code == 404:
            click.echo(f"\N{CROSS MARK} Volume '{name}' not found")
            return
        raise


@volumes.command("list")
@click.pass_context
@handle_api_errors("Volumes")
def volumes_list(ctx: click.Context) -> None:
    """List all volumes"""
    client: Together = ctx.obj
    response = client.beta.jig.volumes.with_raw_response.list()
    click.echo(json.dumps(response.json(), indent=2))
