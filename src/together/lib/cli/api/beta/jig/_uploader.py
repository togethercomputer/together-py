"""Volume management CLI commands for jig."""

from __future__ import annotations

import os
import sys
import time
import asyncio
import itertools
from typing import Any
from pathlib import Path

import httpx
from rich import print as rich_print

from together import Together
from together.lib.utils import log_debug

DEBUG = os.getenv("TOGETHER_DEBUG", "").strip()[:1] in ("y", "1", "t")

UPLOAD_CONCURRENCY_LIMIT = int(os.getenv("TOGETHER_UPLOAD_CONCURRENCY", "15"))
MULTIPART_CHUNK_SIZE_MB = int(os.getenv("TOGETHER_MULTIPART_CHUNK_SIZE_MB", "20"))
MULTIPART_THRESHOLD_MB = int(os.getenv("TOGETHER_MULTIPART_THRESHOLD_MB", "100"))
MAX_UPLOAD_RETRIES = 3
# How many part-sized chunks to read ahead beyond the in-flight uploads
READ_AHEAD_CHUNKS = int(os.getenv("TOGETHER_UPLOAD_READ_AHEAD", "10"))
MAX_IN_MEMORY_CHUNKS = UPLOAD_CONCURRENCY_LIMIT + READ_AHEAD_CHUNKS


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
        # caps how many part-sized chunks are held in memory at once, globally
        self.memory_semaphore: asyncio.Semaphore
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

        msg = f"{spinner} {percent}% - {speed_str}{display_file} {size_str} ({self.completed_files}/{self.total_files} files)"

        # \r moves cursor to start of line, \033[K clears from cursor to end of line.
        # Use the builtin print (rich's print strips the \r) so the line updates
        # in-place instead of appending each progress update.
        print(f"\r{msg}\033[K", end="", flush=True)  # noqa: T201

    async def increment_progress(self, bytes_count: int, filename: str = "", file_complete: bool = False) -> None:
        async with self.progress_lock:
            if bytes_count > 0:
                self.uploaded_bytes += bytes_count
            if DEBUG:
                log_debug(f"bytes_count={bytes_count}, total={self.uploaded_bytes}")
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

    async def upload_files(self, source_path: Path, remote_prefix: str) -> None:
        """Upload all files from source directory with progress tracking"""
        # these require a running event loop
        self.semaphore = asyncio.Semaphore(UPLOAD_CONCURRENCY_LIMIT)
        self.memory_semaphore = asyncio.Semaphore(MAX_IN_MEMORY_CHUNKS)
        self.progress_lock = asyncio.Lock()
        files_to_upload: list[tuple[Path, str, int]] = []

        for file_path in source_path.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(source_path)
                remote_path = f"{remote_prefix}/{rel_path.as_posix()}"
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
        rich_print(f"\n\N{CHECK MARK} Upload completed in {elapsed_time:.1f} seconds")

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
                rich_print(f"[red]Failed to abort multipart upload request: {repr(e)}[/red]", file=sys.stderr)
            raise

    async def _upload_parts(
        self,
        file_path: Path,
        part_urls: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Upload file parts concurrently.

        Chunks are read sequentially and handed to upload tasks already in
        memory, so an upload never waits on disk. ``self.memory_semaphore``
        bounds how many part-sized chunks are resident at once (globally, across
        all files): a slot is reserved before a chunk is read and released once
        its upload finishes, so peak memory stays bounded by
        ``MAX_IN_MEMORY_CHUNKS * chunk_size`` instead of growing with file size.
        """

        async def upload_part(part_info: dict[str, Any], data: bytes) -> dict[str, Any]:
            err = None
            try:
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
            finally:
                self.memory_semaphore.release()

        tasks: list[asyncio.Task[dict[str, Any]]] = []
        with open(file_path, "rb") as f:
            for part_info in part_urls:
                # block until a slot frees, bounding chunks read ahead of uploads
                await self.memory_semaphore.acquire()
                try:
                    data = await asyncio.to_thread(f.read, self.chunk_size)
                except BaseException:
                    self.memory_semaphore.release()
                    raise
                tasks.append(asyncio.create_task(upload_part(part_info, data)))

        completed_parts = await asyncio.gather(*tasks)
        return sorted(completed_parts, key=lambda x: x["part_number"])
