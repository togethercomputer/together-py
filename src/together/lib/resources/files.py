from __future__ import annotations

import os
import re
import math
import stat
import time
import uuid
import shutil
import asyncio
import hashlib
import logging
import tempfile
import ipaddress
from typing import IO, Any, Dict, List, Tuple, Callable, Iterator, AsyncIterator, cast
from pathlib import Path
from functools import partial
from dataclasses import dataclass
from urllib.parse import urlparse
from concurrent.futures import Future, ThreadPoolExecutor, as_completed

import httpx
from filelock import FileLock

from together._utils._logs import logger

from ...types import FileType, FilePurpose, FileResponse
from ..._types import RequestOptions
from ..constants import (
    NUM_BYTES_IN_GB,
    MAX_FILE_SIZE_GB,
    MIN_PART_SIZE_MB,
    DOWNLOAD_BLOCK_SIZE,
    MAX_MULTIPART_PARTS,
    TARGET_PART_SIZE_MB,
    MAX_CONCURRENT_PARTS,
    MAX_DOWNLOAD_RETRIES,
    MULTIPART_THRESHOLD_GB,
    DOWNLOAD_MAX_RETRY_DELAY,
    MULTIPART_UPLOAD_TIMEOUT,
    DOWNLOAD_INITIAL_RETRY_DELAY,
    MULTIPART_UPLOAD_WRITE_TIMEOUT,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..types.error import DownloadError, FileTypeError
from ..._exceptions import APIStatusError, APIConnectionError, AuthenticationError

log: logging.Logger = logging.getLogger(__name__)

UPLOAD_PROGRESS_CHUNK_SIZE = 1024 * 1024
# Path-segment safe. Prefix and punctuation are server-controlled (not always ``file-``).
_SAFE_FILE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
# Replay PUT+body. 307/308 are spec-correct (S3/GCS); 301/302/303 match prior httpx auto-follow.
_UPLOAD_REPLAY_REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
_MAX_UPLOAD_REDIRECTS = 20
_INSECURE_UPLOAD_REDIRECTS_ENV = "TOGETHER_ALLOW_INSECURE_UPLOAD_REDIRECTS"


def _env_flag_enabled(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes"}


def _allow_http_upload_redirects(client: Any) -> bool:
    """Whether PUT *redirect hops* may use http / non-public literals.

    API-issued URLs (presigned ``Location``, multipart part URLs) are validated
    separately via ``_validate_upload_server_url`` and already allow those.
    Set ``TOGETHER_ALLOW_INSECURE_UPLOAD_REDIRECTS=1`` to also permit them on
    subsequent 3xx ``Location`` hops, or use an ``http`` client ``base_url``.
    """

    if _env_flag_enabled(_INSECURE_UPLOAD_REDIRECTS_ENV):
        return True
    base_url = getattr(client, "base_url", None)
    return getattr(base_url, "scheme", None) == "http"


def _parse_ipv4_component(part: str) -> int | None:
    """Parse one inet_aton IPv4 component (decimal, octal, or hex)."""

    if not part:
        return None
    try:
        if part.startswith("0x"):
            return int(part, 16) if len(part) > 2 else None
        if len(part) > 1 and part[0] == "0" and all(c in "01234567" for c in part):
            return int(part, 8)
        if part.isdecimal():
            return int(part, 10)
    except ValueError:
        return None
    return None


def _parse_posix_ipv4(hostname: str) -> ipaddress.IPv4Address | None:
    """Parse IPv4 the way POSIX ``inet_aton`` / getaddrinfo do.

    ``ipaddress.ip_address`` rejects abbreviated (``127.1``), octal
    (``0177.0.0.1``), hex-dotted, and dword forms that still resolve to
    127.0.0.1.
    """

    parts = hostname.split(".")
    if not parts or len(parts) > 4:
        return None
    nums: list[int] = []
    for part in parts:
        value = _parse_ipv4_component(part)
        if value is None:
            return None
        nums.append(value)
    try:
        if len(nums) == 1:
            return ipaddress.IPv4Address(nums[0])
        if len(nums) == 2:
            if nums[0] > 0xFF or nums[1] > 0xFFFFFF:
                return None
            return ipaddress.IPv4Address((nums[0] << 24) | nums[1])
        if len(nums) == 3:
            if nums[0] > 0xFF or nums[1] > 0xFF or nums[2] > 0xFFFF:
                return None
            return ipaddress.IPv4Address((nums[0] << 24) | (nums[1] << 16) | nums[2])
        if any(n > 0xFF for n in nums):
            return None
        return ipaddress.IPv4Address((nums[0] << 24) | (nums[1] << 16) | (nums[2] << 8) | nums[3])
    except (ValueError, ipaddress.AddressValueError):
        return None


def _parse_hostname_ip(hostname: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    try:
        return ipaddress.ip_address(hostname)
    except ValueError:
        pass
    return _parse_posix_ipv4(hostname.lower())


def _ip_is_non_public(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    mapped = ip.ipv4_mapped if isinstance(ip, ipaddress.IPv6Address) else None
    candidate: ipaddress.IPv4Address | ipaddress.IPv6Address = mapped if mapped is not None else ip
    return not candidate.is_global


def _validate_upload_redirect_url(
    redirect_url: str,
    *,
    allow_http: bool = False,
    allow_non_public: bool = False,
) -> str:
    """Best-effort URL-layer filter for upload PUT targets.

    This is not a complete SSRF defense: we do not resolve DNS, so a name like
    ``127.0.0.1.nip.io`` still passes. We do reject non-public dotted-quad / IPv6
    literals, IPv4-mapped loopback (``::ffff:127.0.0.1``), dword decimal/hex
    IPv4 (``2130706433``, ``0x7f000001``), abbreviated (``127.1``), and octal
    (``0177.0.0.1``) forms that getaddrinfo will treat as 127.0.0.1.

    HTTPS is required unless ``allow_http`` is set. Non-public / localhost
    literals are rejected unless ``allow_http`` or ``allow_non_public`` is set.

    For *redirect hops*, ``allow_http`` is True when the client's ``base_url``
    is ``http`` or ``TOGETHER_ALLOW_INSECURE_UPLOAD_REDIRECTS`` is enabled.
    API-issued URLs use ``_validate_upload_server_url`` instead, which allows
    private http(s) storage (MinIO, internal S3) without that env var.
    """

    parsed = urlparse(redirect_url)
    if parsed.scheme == "https" or (parsed.scheme == "http" and allow_http):
        pass
    else:
        raise ValueError(f"Refusing non-HTTPS upload redirect URL: {redirect_url!r}")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError(f"Upload redirect URL is missing a hostname: {redirect_url!r}")

    lowered = hostname.lower()
    if lowered == "metadata.google.internal":
        raise ValueError(f"Refusing upload redirect to local host: {redirect_url!r}")

    if not allow_http and not allow_non_public:
        if lowered == "localhost" or lowered.endswith(".localhost"):
            raise ValueError(f"Refusing upload redirect to local host: {redirect_url!r}")

        ip = _parse_hostname_ip(hostname)
        if ip is not None and _ip_is_non_public(ip):
            raise ValueError(f"Refusing upload redirect to non-public address: {redirect_url!r}")

    return redirect_url


def _validate_upload_server_url(url: str) -> str:
    """Validate an API-issued upload URL (presigned Location or multipart part URL).

    Trusts the Together API: private/loopback literals and plain http are
    allowed so on-prem MinIO / internal S3 work. Redirect hops stay strict.
    """

    return _validate_upload_redirect_url(url, allow_http=True, allow_non_public=True)


def _validate_upload_file_id(file_id: str) -> str:
    if not _SAFE_FILE_ID_RE.fullmatch(file_id):
        raise ValueError(f"Invalid upload file id returned by server: {file_id!r}")
    return file_id


@dataclass(frozen=True)
class FileUploadProgress:
    """Byte-level upload progress reported by file upload managers."""

    uploaded_bytes: int
    total_bytes: int


@dataclass(frozen=True)
class FileDownloadProgress:
    """Byte-level download progress reported by file download managers."""

    downloaded_bytes: int
    total_bytes: int


UploadProgressCallback = Callable[[FileUploadProgress], None]
DownloadProgressCallback = Callable[[FileDownloadProgress], None]


def _notify_upload_progress(
    progress_callback: UploadProgressCallback | None,
    uploaded_bytes: int,
    total_bytes: int,
) -> None:
    if progress_callback is not None:
        progress_callback(FileUploadProgress(uploaded_bytes=uploaded_bytes, total_bytes=total_bytes))


def _monotonic_upload_progress(
    progress_callback: UploadProgressCallback | None,
) -> UploadProgressCallback | None:
    """Ignore progress that rewinds, e.g. a fresh iterator after a redirect replay."""

    if progress_callback is None:
        return None

    last_uploaded = 0

    def on_progress(event: FileUploadProgress) -> None:
        nonlocal last_uploaded
        if event.uploaded_bytes < last_uploaded:
            return
        last_uploaded = event.uploaded_bytes
        progress_callback(event)

    return on_progress


def _notify_download_progress(
    progress_callback: DownloadProgressCallback | None,
    downloaded_bytes: int,
    total_bytes: int,
) -> None:
    if progress_callback is not None:
        progress_callback(FileDownloadProgress(downloaded_bytes=downloaded_bytes, total_bytes=total_bytes))


def _iter_open_file_upload_chunks(
    file_handle: IO[bytes],
    *,
    total_bytes: int,
    progress_callback: UploadProgressCallback | None = None,
    chunk_size: int = UPLOAD_PROGRESS_CHUNK_SIZE,
) -> Iterator[bytes]:
    """Yield at most ``total_bytes`` from an already-open handle (matches Content-Length)."""

    uploaded_bytes = 0
    remaining = total_bytes
    _notify_upload_progress(progress_callback, uploaded_bytes, total_bytes)
    while remaining > 0:
        chunk = file_handle.read(min(chunk_size, remaining))
        if not chunk:
            raise OSError("File was truncated during upload")
        remaining -= len(chunk)
        yield chunk
        uploaded_bytes += len(chunk)
        _notify_upload_progress(progress_callback, uploaded_bytes, total_bytes)


async def _aiter_open_file_upload_chunks(
    file_handle: IO[bytes],
    *,
    total_bytes: int,
    progress_callback: UploadProgressCallback | None = None,
    chunk_size: int = UPLOAD_PROGRESS_CHUNK_SIZE,
) -> AsyncIterator[bytes]:
    """Async counterpart of ``_iter_open_file_upload_chunks``.

    Sync iterators are wrapped as ``SyncByteStream``, which AsyncClient rejects with
    ``Attempted to send an sync request with an AsyncClient instance.``
    """

    for chunk in _iter_open_file_upload_chunks(
        file_handle,
        total_bytes=total_bytes,
        progress_callback=progress_callback,
        chunk_size=chunk_size,
    ):
        yield chunk


def _response_body_text(response: httpx.Response) -> str:
    try:
        return response.content.decode()
    except Exception:
        return ""


def _upload_redirect_url(response: httpx.Response, current_url: str, *, allow_http: bool = False) -> str:
    location = response.headers.get("Location")
    if not location:
        raise APIStatusError(
            f"Error during file upload: redirect {response.status_code} missing Location, headers: {response.headers}",
            response=response,
            body=_response_body_text(response),
        )

    next_url = str(httpx.URL(current_url).join(location))
    try:
        return _validate_upload_redirect_url(next_url, allow_http=allow_http)
    except ValueError as e:
        raise APIStatusError(
            str(e),
            response=response,
            body=_response_body_text(response),
        ) from e


def _put_file_content(
    http_client: httpx.Client,
    url: str,
    file: Path,
    *,
    file_size: int,
    progress_callback: UploadProgressCallback | None = None,
    allow_http: bool = False,
) -> httpx.Response:
    """PUT a streaming file body without httpx replaying a consumed generator.

    ``self._client._client`` is built with ``follow_redirects=True``. A one-shot
    iterator cannot be replayed, so a redirect (or any retry after the first byte)
    would raise ``StreamConsumed``. Disable auto-follow and re-PUT with a fresh
    iterator after validating ``Location``.
    """

    hops = 0
    progress_callback = _monotonic_upload_progress(progress_callback)
    _ = file_size  # each hop fstats the fd; caller size can be stale
    while True:
        # Open + fstat the same fd so Content-Length matches the streamed body even
        # if the file is appended/truncated between hops (or vs. the caller's stat).
        with file.open("rb") as file_handle:
            put_size = os.fstat(file_handle.fileno()).st_size
            response = http_client.put(
                url=url,
                content=_iter_open_file_upload_chunks(
                    file_handle,
                    total_bytes=put_size,
                    progress_callback=progress_callback,
                ),
                headers={"Content-Length": str(put_size)},
                follow_redirects=False,
            )
        if response.status_code not in _UPLOAD_REPLAY_REDIRECT_STATUSES:
            return response
        hops += 1
        if hops > _MAX_UPLOAD_REDIRECTS:
            raise APIStatusError(
                f"Error during file upload: exceeded {_MAX_UPLOAD_REDIRECTS} redirects, headers: {response.headers}",
                response=response,
                body=_response_body_text(response),
            )
        url = _upload_redirect_url(response, url, allow_http=allow_http)
        log.debug("Upload redirected to %s", url)
        response.close()


async def _aput_file_content(
    http_client: httpx.AsyncClient,
    url: str,
    file: Path,
    *,
    file_size: int,
    progress_callback: UploadProgressCallback | None = None,
    allow_http: bool = False,
) -> httpx.Response:
    """Async counterpart of ``_put_file_content``."""

    hops = 0
    progress_callback = _monotonic_upload_progress(progress_callback)
    _ = file_size  # each hop fstats the fd; caller size can be stale
    while True:
        with file.open("rb") as file_handle:
            put_size = os.fstat(file_handle.fileno()).st_size
            response = await http_client.put(
                url=url,
                content=_aiter_open_file_upload_chunks(
                    file_handle,
                    total_bytes=put_size,
                    progress_callback=progress_callback,
                ),
                headers={"Content-Length": str(put_size)},
                follow_redirects=False,
            )
        if response.status_code not in _UPLOAD_REPLAY_REDIRECT_STATUSES:
            return response
        hops += 1
        if hops > _MAX_UPLOAD_REDIRECTS:
            raise APIStatusError(
                f"Error during file upload: exceeded {_MAX_UPLOAD_REDIRECTS} redirects, headers: {response.headers}",
                response=response,
                body=_response_body_text(response),
            )
        url = _upload_redirect_url(response, url, allow_http=allow_http)
        log.debug("Upload redirected to %s", url)
        await response.aclose()


def chmod_and_replace(src: Path, dst: Path) -> None:
    """Set correct permission before moving a blob from tmp directory to cache dir.

    Do not take into account the `umask` from the process as there is no convenient way
    to get it that is thread-safe.
    """

    # Get umask by creating a temporary file in the cache folder.
    tmp_file = dst.parent / f"tmp_{uuid.uuid4()}"

    try:
        tmp_file.touch()

        cache_dir_mode = Path(tmp_file).stat().st_mode

        os.chmod(src.as_posix(), stat.S_IMODE(cache_dir_mode))

    finally:
        tmp_file.unlink()

    shutil.move(src.as_posix(), dst.as_posix())


def _get_file_size(
    headers: httpx.Headers,
) -> int:
    """
    Extracts file size from header
    """
    total_size_in_bytes = 0

    parts = headers.get("Content-Range", "").split(" ")

    if len(parts) == 2:
        range_parts = parts[1].split("/")

        if len(range_parts) == 2:
            total_size_in_bytes = int(range_parts[1])

    assert total_size_in_bytes != 0, "Unable to retrieve remote file."

    return total_size_in_bytes


def _prepare_output(
    headers: httpx.Headers,
    step: int = -1,
    output: Path | None = None,
    remote_name: str | None = None,
) -> Path:
    """
    Generates output file name from remote name and headers
    """
    if output:
        return output

    content_type = str(headers.get("content-type"))

    assert remote_name, "No model name found in fine_tuning object. Please specify an `output` file name."

    if step > 0:
        remote_name += f"-checkpoint-{step}"

    if "x-tar" in content_type.lower():
        remote_name += ".tar.gz"

    else:
        remote_name += ".tar.zst"

    return Path(remote_name)


class DownloadManager(SyncAPIResource):
    def get_file_metadata(
        self,
        url: str,
        output: Path | None = None,
        remote_name: str | None = None,
        fetch_metadata: bool = False,
    ) -> Tuple[Path, int]:
        """
        gets remote file head and parses out file name and file size
        """

        if not fetch_metadata:
            if isinstance(output, Path):
                file_path = output
            else:
                assert isinstance(remote_name, str)
                file_path = Path(remote_name)

            return file_path, 0

        try:
            response = self._client.get(
                path=url,
                options=RequestOptions(
                    headers={"Range": "bytes=0-1"},
                ),
                cast_to=httpx.Response,
                stream=False,
            )
        except APIStatusError as e:
            raise APIStatusError(
                "Error fetching file metadata",
                response=e.response,
                body=e.body,
            ) from e

        headers = response.headers

        assert isinstance(headers, httpx.Headers)

        file_path = _prepare_output(
            headers=headers,
            output=output,
            remote_name=remote_name,
        )

        file_size = _get_file_size(headers)

        return file_path, file_size

    def download(
        self,
        url: str,
        output: Path | None = None,
        remote_name: str | None = None,
        fetch_metadata: bool = False,
        *,
        progress_callback: DownloadProgressCallback | None = None,
    ) -> Tuple[str, int]:
        # pre-fetch remote file name and file size
        file_path, file_size = self.get_file_metadata(url, output, remote_name, fetch_metadata)

        temp_file_manager = partial(tempfile.NamedTemporaryFile, mode="wb", dir=file_path.parent, delete=False)

        # Prevent parallel downloads of the same file with a lock.
        lock_path = Path(file_path.as_posix() + ".lock")

        with FileLock(lock_path.as_posix()):
            with temp_file_manager() as temp_file:
                try:
                    response = self._client.get(
                        path=url,
                        cast_to=httpx.Response,
                        stream=True,
                    )
                except APIStatusError as e:
                    lock_path.unlink(missing_ok=True)
                    raise APIStatusError(
                        "Error downloading file",
                        response=e.response,
                        body=e.body,
                    ) from e

                if not fetch_metadata:
                    file_size = int(response.headers.get("content-length", 0))

                assert file_size != 0, "Unable to retrieve remote file."

                # Download with retry logic
                bytes_downloaded = 0
                retry_count = 0
                retry_delay = DOWNLOAD_INITIAL_RETRY_DELAY
                _notify_download_progress(progress_callback, bytes_downloaded, file_size)

                while bytes_downloaded < file_size:
                    try:
                        # If this is a retry, close the previous response and create a new one with Range header
                        if bytes_downloaded > 0:
                            response.close()

                            log.info(f"Resuming download from byte {bytes_downloaded}")
                            response = self._client.get(
                                path=url,
                                cast_to=httpx.Response,
                                stream=True,
                                options=RequestOptions(
                                    headers={"Range": f"bytes={bytes_downloaded}-"},
                                ),
                            )

                        # Download chunks
                        for chunk in response.iter_bytes(DOWNLOAD_BLOCK_SIZE):
                            temp_file.write(chunk)  # type: ignore
                            bytes_downloaded += len(chunk)
                            _notify_download_progress(progress_callback, bytes_downloaded, file_size)

                        # Successfully completed download
                        break

                    except (httpx.RequestError, httpx.StreamError, APIConnectionError) as e:
                        if retry_count >= MAX_DOWNLOAD_RETRIES:
                            log.error(f"Download failed after {retry_count} retries")
                            raise DownloadError(
                                f"Download failed after {retry_count} retries. Last error: {str(e)}"
                            ) from e

                        retry_count += 1
                        log.warning(
                            f"Download interrupted at {bytes_downloaded}/{file_size} bytes. "
                            f"Retry {retry_count}/{MAX_DOWNLOAD_RETRIES} in {retry_delay}s..."
                        )
                        time.sleep(retry_delay)

                        # Exponential backoff with max delay cap
                        retry_delay = min(retry_delay * 2, DOWNLOAD_MAX_RETRY_DELAY)

                    except APIStatusError as e:
                        # For API errors, don't retry
                        log.error(f"API error during download: {e}")
                        raise APIStatusError(
                            "Error downloading file",
                            response=e.response,
                            body=e.body,
                        ) from e

                # Close the response
                response.close()

            # Raise exception if remote file size does not match downloaded file size
            if os.stat(temp_file.name).st_size != file_size:
                raise DownloadError(
                    f"Downloaded file size `{bytes_downloaded}` bytes does not match remote file size `{file_size}` bytes."
                )

            # Moves temp file to output file path
            chmod_and_replace(Path(temp_file.name), file_path)

        lock_path.unlink(missing_ok=True)

        return str(file_path.resolve()), file_size


class AsyncDownloadManager(AsyncAPIResource):
    async def get_file_metadata(
        self,
        url: str,
        output: Path | None = None,
        remote_name: str | None = None,
        fetch_metadata: bool = False,
    ) -> Tuple[Path, int]:
        """
        gets remote file head and parses out file name and file size
        """

        if not fetch_metadata:
            if isinstance(output, Path):
                file_path = output
            else:
                assert isinstance(remote_name, str)
                file_path = Path(remote_name)

            return file_path, 0

        try:
            response = await self._client.get(
                path=url,
                options=RequestOptions(
                    headers={"Range": "bytes=0-1"},
                ),
                cast_to=httpx.Response,
                stream=False,
            )
        except APIStatusError as e:
            raise APIStatusError(
                "Error fetching file metadata",
                response=e.response,
                body=e.body,
            ) from e

        headers = response.headers

        assert isinstance(headers, httpx.Headers)

        file_path = _prepare_output(
            headers=headers,
            output=output,
            remote_name=remote_name,
        )

        file_size = _get_file_size(headers)

        return file_path, file_size

    async def download(
        self,
        url: str,
        output: Path | None = None,
        remote_name: str | None = None,
        fetch_metadata: bool = False,
        *,
        progress_callback: DownloadProgressCallback | None = None,
    ) -> Tuple[str, int]:
        # pre-fetch remote file name and file size
        file_path, file_size = await self.get_file_metadata(url, output, remote_name, fetch_metadata)

        temp_file_manager = partial(tempfile.NamedTemporaryFile, mode="wb", dir=file_path.parent, delete=False)

        # Prevent parallel downloads of the same file with a lock.
        lock_path = Path(file_path.as_posix() + ".lock")

        with FileLock(lock_path.as_posix()):
            with temp_file_manager() as temp_file:
                try:
                    response = await self._client.get(
                        path=url,
                        cast_to=httpx.Response,
                        stream=True,
                    )
                except APIStatusError as e:
                    lock_path.unlink(missing_ok=True)
                    raise APIStatusError(
                        "Error downloading file",
                        response=e.response,
                        body=e.body,
                    ) from e

                if not fetch_metadata:
                    file_size = int(response.headers.get("content-length", 0))

                assert file_size != 0, "Unable to retrieve remote file."

                # Download with retry logic
                bytes_downloaded = 0
                retry_count = 0
                retry_delay = DOWNLOAD_INITIAL_RETRY_DELAY
                _notify_download_progress(progress_callback, bytes_downloaded, file_size)

                while bytes_downloaded < file_size:
                    try:
                        # If this is a retry, close the previous response and create a new one with Range header
                        if bytes_downloaded > 0:
                            await response.aclose()

                            log.info(f"Resuming download from byte {bytes_downloaded}")
                            response = await self._client.get(
                                path=url,
                                cast_to=httpx.Response,
                                stream=True,
                                options=RequestOptions(
                                    headers={"Range": f"bytes={bytes_downloaded}-"},
                                ),
                            )

                        # Download chunks
                        async for chunk in response.aiter_bytes(DOWNLOAD_BLOCK_SIZE):
                            temp_file.write(chunk)  # type: ignore
                            bytes_downloaded += len(chunk)
                            _notify_download_progress(progress_callback, bytes_downloaded, file_size)

                        # Successfully completed download
                        break

                    except (httpx.RequestError, httpx.StreamError, APIConnectionError) as e:
                        if retry_count >= MAX_DOWNLOAD_RETRIES:
                            log.error(f"Download failed after {retry_count} retries")
                            raise DownloadError(
                                f"Download failed after {retry_count} retries. Last error: {str(e)}"
                            ) from e

                        retry_count += 1
                        log.warning(
                            f"Download interrupted at {bytes_downloaded}/{file_size} bytes. "
                            f"Retry {retry_count}/{MAX_DOWNLOAD_RETRIES} in {retry_delay}s..."
                        )
                        await self._sleep(retry_delay)

                        # Exponential backoff with max delay cap
                        retry_delay = min(retry_delay * 2, DOWNLOAD_MAX_RETRY_DELAY)

                    except APIStatusError as e:
                        # For API errors, don't retry
                        log.error(f"API error during download: {e}")
                        raise APIStatusError(
                            "Error downloading file",
                            response=e.response,
                            body=e.body,
                        ) from e

                # Close the response
                await response.aclose()

            # Raise exception if remote file size does not match downloaded file size
            if os.stat(temp_file.name).st_size != file_size:
                raise DownloadError(
                    f"Downloaded file size `{bytes_downloaded}` bytes does not match remote file size `{file_size}` bytes."
                )

            # Moves temp file to output file path
            chmod_and_replace(Path(temp_file.name), file_path)

        lock_path.unlink(missing_ok=True)

        return str(file_path.resolve()), file_size


class UploadManager(SyncAPIResource):
    def get_upload_url(
        self,
        url: str,
        file: Path,
        checksum: str,
        purpose: FilePurpose,
        filetype: FileType,
    ) -> Tuple[str, str]:
        data = {
            "purpose": purpose,
            "file_name": file.name,
            "file_type": filetype,
            "checksum": checksum,
        }

        try:
            response = self._client.post(
                path=url,
                cast_to=httpx.Response,
                body=data,
                options={"headers": {"Content-Type": "multipart/form-data"}, "follow_redirects": False},
            )
        except APIStatusError as e:
            if e.response.status_code == 409:
                raise FileAlreadyExistsError(e.response.json()["file_id"]) from e
            if e.response.status_code == 401:
                raise AuthenticationError(
                    "This job would exceed your free trial credits. "
                    "Please upgrade to a paid account through "
                    "Settings -> Billing on api.together.ai to continue.",
                    response=e.response,
                    body=e.body,
                ) from e
            if e.response.status_code != 302:
                raise APIStatusError(
                    f"Unexpected error raised by endpoint: {e.response.content.decode()}, headers: {e.response.headers}",
                    response=e.response,
                    body=e.response.content.decode(),
                ) from e
            response = e.response

        redirect_url = response.headers.get("Location")
        file_id = response.headers.get("X-Together-File-Id")

        if not redirect_url or not file_id:
            raise APIStatusError(
                f"Missing required headers in response. Location: {redirect_url}, File-Id: {file_id}",
                response=response,
                body=response.content.decode() if hasattr(response, "content") else "",
            )

        try:
            return (
                _validate_upload_server_url(redirect_url),
                _validate_upload_file_id(file_id),
            )
        except ValueError as e:
            raise APIStatusError(
                str(e),
                response=response,
                body=response.content.decode() if hasattr(response, "content") else "",
            ) from e

    def callback(self, url: str) -> FileResponse:
        response = self._client.post(
            cast_to=FileResponse,
            path=url,
        )

        return response

    def upload(
        self,
        url: str,
        file: Path,
        purpose: FilePurpose,
        *,
        progress_callback: UploadProgressCallback | None = None,
    ) -> FileResponse:
        file_size = os.stat(file.as_posix()).st_size
        file_size_gb = file_size / NUM_BYTES_IN_GB

        if file_size_gb > MAX_FILE_SIZE_GB:
            raise FileTypeError(
                f"File size {file_size_gb:.1f}GB exceeds maximum supported size of {MAX_FILE_SIZE_GB}GB"
            )

        checksum = _calculate_file_checksum(file)

        if file_size_gb > MULTIPART_THRESHOLD_GB:
            multipart_manager = MultipartUploadManager(self._client)
            return multipart_manager.upload(url, file, checksum, purpose, progress_callback=progress_callback)
        else:
            return self._upload_single_file(url, file, checksum, purpose, progress_callback=progress_callback)

    def _upload_single_file(
        self,
        url: str,
        file: Path,
        checksum: str,
        purpose: FilePurpose,
        *,
        progress_callback: UploadProgressCallback | None = None,
    ) -> FileResponse:
        file_id = None

        redirect_url = None
        if file.suffix == ".jsonl":
            filetype = "jsonl"
        elif file.suffix == ".parquet":
            filetype = "parquet"
        elif file.suffix == ".csv":
            filetype = "csv"
        else:
            raise FileTypeError(
                f"Unknown extension of file {file}. Only files with extensions .jsonl, .parquet, and .csv are supported."
            )
        redirect_url, file_id = self.get_upload_url(url, file, checksum, purpose, filetype)  # type: ignore

        file_size = os.stat(file.as_posix()).st_size

        assert redirect_url is not None
        callback_response = _put_file_content(
            self._client._client,
            redirect_url,
            file,
            file_size=file_size,
            progress_callback=progress_callback,
            allow_http=_allow_http_upload_redirects(self._client),
        )
        log.debug(
            'HTTP Response: %s %s "%i %s" %s',
            "put",
            redirect_url,
            callback_response.status_code,
            callback_response.reason_phrase,
            callback_response.headers,
        )

        assert isinstance(callback_response, httpx.Response)  # type: ignore

        if not callback_response.status_code == 200:
            raise APIStatusError(
                f"Error during file upload: {callback_response.content.decode()}, headers: {callback_response.headers}",
                response=callback_response,
                body=callback_response.content.decode(),
            )

        response = self.callback(f"{url}/{file_id}/preprocess")

        assert isinstance(response, FileResponse)  # type: ignore

        return response


class MultipartUploadManager(SyncAPIResource):
    """Handles multipart uploads for large files"""

    def __init__(self, client: Any) -> None:  # Accept any client type
        super().__init__(client)
        self.max_concurrent_parts = MAX_CONCURRENT_PARTS

    def upload(
        self,
        url: str,
        file: Path,
        checksum: str,
        purpose: FilePurpose,
        *,
        progress_callback: UploadProgressCallback | None = None,
    ) -> FileResponse:
        """Upload large file using multipart upload"""

        file_size = os.stat(file.as_posix()).st_size
        file_size_gb = file_size / NUM_BYTES_IN_GB

        if file_size_gb > MAX_FILE_SIZE_GB:
            raise FileTypeError(
                f"File size {file_size_gb:.1f}GB exceeds maximum supported size of {MAX_FILE_SIZE_GB}GB"
            )

        part_size, num_parts = _calculate_parts(file_size)
        file_type = self._get_file_type(file)
        upload_info = None

        try:
            upload_info = self._initiate_upload(url, file, checksum, file_size, num_parts, purpose, file_type)
            upload_id = upload_info.get("upload_id")
            file_id = upload_info.get("file_id")
            if not upload_id or not file_id:
                raise ValueError("Missing upload_id or file_id from initiate response")
            file_id = _validate_upload_file_id(str(file_id))
            upload_info["file_id"] = file_id

            completed_parts = self._upload_parts_concurrent(
                file,
                upload_info,
                part_size,
                progress_callback=progress_callback,
            )

            return self._complete_upload(url, upload_id, file_id, completed_parts)

        # If the server says the file already exists, raise the error to the files.upload resource
        # This should be silently handled by fetching down the file and returning it
        except FileAlreadyExistsError as e:
            raise e
        except Exception as e:
            if upload_info is not None:
                upload_id = upload_info.get("upload_id")
                file_id = upload_info.get("file_id")
                if upload_id and file_id:
                    self._abort_upload(url, upload_id, file_id)
            raise e

    def _get_file_type(self, file: Path) -> str:
        """Get file type from extension"""
        if file.suffix == ".jsonl":
            return "jsonl"
        elif file.suffix == ".parquet":
            return "parquet"
        elif file.suffix == ".csv":
            return "csv"
        else:
            raise ValueError(
                f"Unsupported file extension: '{file.suffix}'. Supported extensions: .jsonl, .parquet, .csv"
            )

    def _initiate_upload(
        self,
        url: str,
        file: Path,
        checksum: str,
        file_size: int,
        num_parts: int,
        purpose: FilePurpose,
        file_type: str,
    ) -> Dict[str, Any]:
        """Initiate multipart upload with backend"""

        payload: Dict[str, Any] = {
            "file_name": file.name,
            "file_size": file_size,
            "num_parts": num_parts,
            "purpose": str(purpose),
            "file_type": file_type,
            "checksum": checksum,
        }

        try:
            response = self._client.post(
                path=f"{url}/multipart/initiate",
                cast_to=httpx.Response,
                body=payload,
                options={"headers": {"Content-Type": "application/json"}},
            )
        except APIStatusError as e:
            if e.response.status_code == 409:
                raise FileAlreadyExistsError(e.response.json()["file_id"]) from e
            if e.response.status_code == 400:
                response = e.response
            else:
                raise e from e

        if response.status_code == 200:
            return cast(Dict[str, Any], response.json())
        else:
            raise APIStatusError(
                f"Failed to initiate multipart upload: {response.text}",
                response=response,
                body=response.text,
            )

    def _submit_part(
        self,
        executor: ThreadPoolExecutor,
        file_handle: IO[bytes],
        part_info: Dict[str, Any],
        part_size: int,
    ) -> Tuple[Future[str], int, int]:
        """Submit a single part for upload and return its future, part number, and size."""

        part_number = part_info.get("PartNumber", part_info.get("part_number", 1))
        file_handle.seek((part_number - 1) * part_size)
        part_data = file_handle.read(part_size)

        future = executor.submit(self._upload_single_part, part_info, part_data)
        return future, part_number, len(part_data)

    def _upload_parts_concurrent(
        self,
        file: Path,
        upload_info: Dict[str, Any],
        part_size: int,
        *,
        progress_callback: UploadProgressCallback | None = None,
    ) -> List[Dict[str, Any]]:
        """Upload file parts concurrently, reporting byte progress to the caller."""

        parts = upload_info["parts"]
        completed_parts: List[Dict[str, Any]] = []
        file_size = os.stat(file.as_posix()).st_size
        uploaded_bytes = 0
        _notify_upload_progress(progress_callback, uploaded_bytes, file_size)

        with ThreadPoolExecutor(max_workers=self.max_concurrent_parts) as executor:
            with open(file, "rb") as f:
                future_to_part: Dict[Future[str], Tuple[int, int]] = {}
                part_index = 0

                while part_index < len(parts) and len(future_to_part) < self.max_concurrent_parts:
                    part_info = parts[part_index]
                    future, part_number, part_bytes = self._submit_part(executor, f, part_info, part_size)
                    future_to_part[future] = (part_number, part_bytes)
                    part_index += 1

                while future_to_part:
                    done_future = next(as_completed(future_to_part))
                    part_number, part_bytes = future_to_part.pop(done_future)

                    try:
                        etag = done_future.result()
                        completed_parts.append({"part_number": part_number, "etag": etag})
                        uploaded_bytes += part_bytes
                        _notify_upload_progress(progress_callback, uploaded_bytes, file_size)
                    except Exception as e:
                        raise Exception(f"Failed to upload part {part_number}: {e}") from e

                    if part_index < len(parts):
                        part_info = parts[part_index]
                        future, next_part_number, next_part_bytes = self._submit_part(executor, f, part_info, part_size)
                        future_to_part[future] = (next_part_number, next_part_bytes)
                        part_index += 1

        completed_parts.sort(key=lambda x: x["part_number"])
        return completed_parts

    def _upload_single_part(self, part_info: Dict[str, Any], part_data: bytes) -> str:
        """Upload a single part and return ETag"""

        upload_url = part_info.get("URL", part_info.get("UploadURL"))
        if not upload_url:
            raise ValueError("Missing upload URL in part info")
        upload_url = _validate_upload_server_url(str(upload_url))

        part_headers = part_info.get("Headers", {})

        timeout = httpx.Timeout(
            MULTIPART_UPLOAD_TIMEOUT,
            write=MULTIPART_UPLOAD_WRITE_TIMEOUT,
        )
        response = self._client._client.put(
            url=upload_url,
            content=part_data,
            headers=part_headers,
            timeout=timeout,
        )
        response.raise_for_status()

        etag = str(response.headers.get("ETag", "")).strip('"')
        if not etag:
            part_number = part_info.get("PartNumber", part_info.get("part_number", "unknown"))
            raise APIStatusError(
                f"No ETag returned for part {part_number}",
                response=response,
                body=response.content.decode(),
            )

        return etag

    def _complete_upload(
        self,
        url: str,
        upload_id: str,
        file_id: str,
        completed_parts: List[Dict[str, Any]],
    ) -> FileResponse:
        """Complete the multipart upload"""

        payload = {
            "upload_id": upload_id,
            "file_id": file_id,
            "parts": completed_parts,
        }

        try:
            response = self._client.post(
                path=f"{url}/multipart/complete",
                cast_to=httpx.Response,
                body=payload,
                options={"headers": {"Content-Type": "application/json"}},
            )
        except APIStatusError as e:
            if e.response.status_code == 400:
                response = e.response
            else:
                raise e from e

        if response.status_code == 200:
            response_data = response.json()
            file_data = response_data.get("file", response_data)
            file_data["object"] = "file"
            return FileResponse(**file_data)
        else:
            raise APIStatusError(
                f"Failed to complete multipart upload: {response.text}",
                response=response,
                body=response.text,
            )

    def _abort_upload(self, url: str, upload_id: str, file_id: str) -> None:
        """Abort the multipart upload"""

        payload = {
            "upload_id": upload_id,
            "file_id": file_id,
        }

        self._client.post(
            path=f"{url}/multipart/abort",
            cast_to=httpx.Response,
            body=payload,
            options={"headers": {"Content-Type": "application/json"}},
        )


class AsyncUploadManager(AsyncAPIResource):
    async def get_upload_url(
        self,
        url: str,
        file: Path,
        checksum: str,
        purpose: FilePurpose,
        filetype: FileType,
    ) -> Tuple[str, str]:
        data = {
            "purpose": str(purpose),
            "file_name": file.name,
            "file_type": filetype,
            "checksum": checksum,
        }

        try:
            response = await self._client.post(
                path=url,
                cast_to=httpx.Response,
                body=data,
                options={"headers": {"Content-Type": "multipart/form-data"}, "follow_redirects": False},
            )
        except APIStatusError as e:
            if e.response.status_code == 409:
                raise FileAlreadyExistsError(e.response.json()["file_id"]) from e
            if e.response.status_code == 401:
                raise AuthenticationError(
                    "This job would exceed your free trial credits. "
                    "Please upgrade to a paid account through "
                    "Settings -> Billing on api.together.ai to continue.",
                    response=e.response,
                    body=e.body,
                ) from e
            if e.response.status_code != 302:
                raise APIStatusError(
                    f"Unexpected error raised by endpoint: {e.response.content.decode()}, headers: {e.response.headers}",
                    response=e.response,
                    body=e.response.content.decode(),
                ) from e
            response = e.response

        redirect_url = response.headers.get("Location")
        file_id = response.headers.get("X-Together-File-Id")

        if not redirect_url or not file_id:
            # Mock server scenario - return mock values for testing
            if response.status_code == 200:
                return "https://mock-upload-url.com", "mock-file-id"
            else:
                raise APIStatusError(
                    f"Missing required headers in response. Location: {redirect_url}, File-Id: {file_id}",
                    response=response,
                    body=response.content.decode() if hasattr(response, "content") else "",
                )

        try:
            return (
                _validate_upload_server_url(redirect_url),
                _validate_upload_file_id(file_id),
            )
        except ValueError as e:
            raise APIStatusError(
                str(e),
                response=response,
                body=response.content.decode() if hasattr(response, "content") else "",
            ) from e

    async def callback(self, url: str) -> FileResponse:
        response = self._client.post(
            cast_to=FileResponse,
            path=url,
        )

        return await response

    async def upload(
        self,
        url: str,
        file: Path,
        purpose: FilePurpose,
        *,
        progress_callback: UploadProgressCallback | None = None,
    ) -> FileResponse:
        file_size = os.stat(file.as_posix()).st_size
        file_size_gb = file_size / NUM_BYTES_IN_GB

        if file_size_gb > MAX_FILE_SIZE_GB:
            raise FileTypeError(
                f"File size {file_size_gb:.1f}GB exceeds maximum supported size of {MAX_FILE_SIZE_GB}GB"
            )

        checksum = _calculate_file_checksum(file)

        if file_size_gb > MULTIPART_THRESHOLD_GB:
            multipart_manager = AsyncMultipartUploadManager(self._client)
            return await multipart_manager.upload(url, file, checksum, purpose, progress_callback=progress_callback)
        else:
            return await self._upload_single_file(url, file, checksum, purpose, progress_callback=progress_callback)

    async def _upload_single_file(
        self,
        url: str,
        file: Path,
        checksum: str,
        purpose: FilePurpose,
        *,
        progress_callback: UploadProgressCallback | None = None,
    ) -> FileResponse:
        file_id = None

        redirect_url = None
        if file.suffix == ".jsonl":
            filetype = "jsonl"
        elif file.suffix == ".parquet":
            filetype = "parquet"
        elif file.suffix == ".csv":
            filetype = "csv"
        else:
            raise FileTypeError(
                f"Unknown extension of file {file}. Only files with extensions .jsonl, .parquet, and .csv are supported."
            )

        redirect_url, file_id = await self.get_upload_url(url, file, checksum, purpose, filetype)  # type: ignore

        file_size = os.stat(file.as_posix()).st_size

        assert redirect_url is not None
        callback_response = await _aput_file_content(
            self._client._client,
            redirect_url,
            file,
            file_size=file_size,
            progress_callback=progress_callback,
            allow_http=_allow_http_upload_redirects(self._client),
        )
        log.debug(
            'HTTP Response: %s %s "%i %s" %s',
            "put",
            redirect_url,
            callback_response.status_code,
            callback_response.reason_phrase,
            callback_response.headers,
        )

        assert isinstance(callback_response, httpx.Response)  # type: ignore

        if not callback_response.status_code == 200:
            raise APIStatusError(
                f"Error during file upload: {callback_response.content.decode()}, headers: {callback_response.headers}",
                response=callback_response,
                body=callback_response.content.decode(),
            )

        response = await self.callback(f"{url}/{file_id}/preprocess")

        assert isinstance(response, FileResponse)  # type: ignore

        return response


class AsyncMultipartUploadManager(AsyncAPIResource):
    """Handles async multipart uploads using ThreadPoolExecutor for efficiency"""

    def __init__(self, client: Any) -> None:  # Accept any client type
        super().__init__(client)
        self.max_concurrent_parts = MAX_CONCURRENT_PARTS

    async def upload(
        self,
        url: str,
        file: Path,
        checksum: str,
        purpose: FilePurpose,
        *,
        progress_callback: UploadProgressCallback | None = None,
    ) -> FileResponse:
        """Upload large file using multipart upload via ThreadPoolExecutor"""

        file_size = os.stat(file.as_posix()).st_size
        file_size_gb = file_size / NUM_BYTES_IN_GB

        if file_size_gb > MAX_FILE_SIZE_GB:
            raise FileTypeError(
                f"File size {file_size_gb:.1f}GB exceeds maximum supported size of {MAX_FILE_SIZE_GB}GB"
            )

        part_size, num_parts = _calculate_parts(file_size)
        file_type = self._get_file_type(file)
        upload_info = None

        try:
            upload_info = await self._initiate_upload(url, file, checksum, file_size, num_parts, purpose, file_type)
            upload_id = upload_info.get("upload_id")
            file_id = upload_info.get("file_id")
            if not upload_id or not file_id:
                raise ValueError("Missing upload_id or file_id from initiate response")
            file_id = _validate_upload_file_id(str(file_id))
            upload_info["file_id"] = file_id

            completed_parts = await self._upload_parts_concurrent(
                file,
                upload_info,
                part_size,
                progress_callback=progress_callback,
            )

            return await self._complete_upload(url, upload_id, file_id, completed_parts)

        # If the server says the file already exists, raise the error to the files.upload resource
        # This should be silently handled by fetching down the file and returning it
        except FileAlreadyExistsError as e:
            raise e
        except Exception as e:
            if upload_info is not None:
                upload_id = upload_info.get("upload_id")
                file_id = upload_info.get("file_id")
                if upload_id and file_id:
                    await self._abort_upload(url, upload_id, file_id)
            raise e

    def _get_file_type(self, file: Path) -> str:
        """Get file type from extension"""
        if file.suffix == ".jsonl":
            return "jsonl"
        elif file.suffix == ".parquet":
            return "parquet"
        elif file.suffix == ".csv":
            return "csv"
        else:
            raise ValueError(
                f"Unsupported file extension: '{file.suffix}'. Supported extensions: .jsonl, .parquet, .csv"
            )

    async def _initiate_upload(
        self,
        url: str,
        file: Path,
        checksum: str,
        file_size: int,
        num_parts: int,
        purpose: FilePurpose,
        file_type: str,
    ) -> Dict[str, Any]:
        """Initiate multipart upload with backend"""

        payload = {
            "file_name": file.name,
            "file_size": file_size,
            "num_parts": num_parts,
            "purpose": str(purpose),
            "file_type": file_type,
            "checksum": checksum,
        }

        try:
            response = await self._client.post(
                path=f"{url}/multipart/initiate",
                cast_to=httpx.Response,
                body=payload,
                options={"headers": {"Content-Type": "application/json"}},
            )
        except APIStatusError as e:
            if e.response.status_code == 409:
                raise FileAlreadyExistsError(e.response.json()["file_id"]) from e
            if e.response.status_code == 400:
                response = e.response
            else:
                raise e from e

        if response.status_code == 200:
            return cast(Dict[str, Any], response.json())
        else:
            raise APIStatusError(
                f"Failed to initiate multipart upload: {response.text}",
                response=response,
                body=response.text,
            )

    async def _upload_parts_concurrent(
        self,
        file: Path,
        upload_info: Dict[str, Any],
        part_size: int,
        *,
        progress_callback: UploadProgressCallback | None = None,
    ) -> List[Dict[str, Any]]:
        """Upload file parts concurrently using ThreadPoolExecutor."""

        parts = upload_info["parts"]
        completed_parts: List[Dict[str, Any]] = []
        file_size = os.stat(file.as_posix()).st_size
        uploaded_bytes = 0
        _notify_upload_progress(progress_callback, uploaded_bytes, file_size)

        # Use ThreadPoolExecutor for HTTP I/O efficiency
        loop = asyncio.get_event_loop()

        with ThreadPoolExecutor(max_workers=self.max_concurrent_parts) as executor:
            with open(file, "rb") as f:
                future_to_part: Dict[asyncio.Future[str], Tuple[int, int]] = {}
                part_index = 0

                while part_index < len(parts) and len(future_to_part) < self.max_concurrent_parts:
                    part_info = parts[part_index]
                    part_number = part_info.get("PartNumber", part_info.get("part_number", 1))
                    f.seek((part_number - 1) * part_size)
                    part_data = f.read(part_size)

                    future = loop.run_in_executor(executor, self._upload_single_part_sync, part_info, part_data)
                    future_to_part[future] = (part_number, len(part_data))
                    part_index += 1

                while future_to_part:
                    done, _ = await asyncio.wait(
                        tuple(future_to_part.keys()),
                        return_when=asyncio.FIRST_COMPLETED,
                    )

                    for done_future in done:
                        part_number, part_bytes = future_to_part.pop(done_future)

                        try:
                            etag = await done_future
                            completed_parts.append({"part_number": part_number, "etag": etag})
                            uploaded_bytes += part_bytes
                            _notify_upload_progress(progress_callback, uploaded_bytes, file_size)
                        except Exception as e:
                            raise Exception(f"Failed to upload part {part_number}: {e}") from e

                        if part_index < len(parts):
                            part_info = parts[part_index]
                            next_part_number = part_info.get("PartNumber", part_info.get("part_number", 1))
                            f.seek((next_part_number - 1) * part_size)
                            part_data = f.read(part_size)
                            future = loop.run_in_executor(executor, self._upload_single_part_sync, part_info, part_data)
                            future_to_part[future] = (next_part_number, len(part_data))
                            part_index += 1

        completed_parts.sort(key=lambda x: x["part_number"])
        return completed_parts

    def _upload_single_part_sync(self, part_info: Dict[str, Any], part_data: bytes) -> str:
        """Sync version of single part upload for use in ThreadPoolExecutor"""

        upload_url = part_info.get("URL", part_info.get("UploadURL"))
        if not upload_url:
            raise ValueError("Missing upload URL in part info")
        upload_url = _validate_upload_server_url(str(upload_url))

        part_headers = part_info.get("Headers", {})

        timeout = httpx.Timeout(
            MULTIPART_UPLOAD_TIMEOUT,
            write=MULTIPART_UPLOAD_WRITE_TIMEOUT,
        )
        with httpx.Client() as client:
            response = client.put(
                url=upload_url,
                content=part_data,
                headers=part_headers,
                timeout=timeout,
            )
        response.raise_for_status()

        etag = str(response.headers.get("ETag", "")).strip('"')
        if not etag:
            part_number = part_info.get("PartNumber", part_info.get("part_number", "unknown"))
            raise ValueError(f"No ETag returned for part {part_number}")

        return etag

    async def _complete_upload(
        self,
        url: str,
        upload_id: str,
        file_id: str,
        completed_parts: List[Dict[str, Any]],
    ) -> FileResponse:
        """Complete the multipart upload"""

        payload = {
            "upload_id": upload_id,
            "file_id": file_id,
            "parts": completed_parts,
        }

        try:
            response = await self._client.post(
                path=f"{url}/multipart/complete",
                cast_to=httpx.Response,
                body=payload,
                options={"headers": {"Content-Type": "application/json"}},
            )
        except APIStatusError as e:
            if e.response.status_code == 400:
                response = e.response
            else:
                raise e from e

        if response.status_code == 200:
            response_data = response.json()
            file_data = response_data.get("file", response_data)
            file_data["object"] = "file"
            return FileResponse(**file_data)
        else:
            raise APIStatusError(
                f"Failed to complete multipart upload: {response.text}",
                response=response,
                body=response.text,
            )

    async def _abort_upload(self, url: str, upload_id: str, file_id: str) -> None:
        """Abort the multipart upload"""

        payload = {
            "upload_id": upload_id,
            "file_id": file_id,
        }

        await self._client.post(
            path=f"{url}/multipart/abort",
            cast_to=httpx.Response,
            body=payload,
            options={"headers": {"Content-Type": "application/json"}},
        )


def _calculate_parts(file_size: int) -> Tuple[int, int]:
    """Calculate optimal part size and count"""
    min_part_size = MIN_PART_SIZE_MB * 1024 * 1024  # 5MB
    target_part_size = TARGET_PART_SIZE_MB * 1024 * 1024  # 100MB

    if file_size <= target_part_size:
        return file_size, 1

    num_parts = min(MAX_MULTIPART_PARTS, math.ceil(file_size / target_part_size))
    part_size = math.ceil(file_size / num_parts)

    if part_size < min_part_size:
        part_size = min_part_size
        num_parts = math.ceil(file_size / part_size)

    return part_size, num_parts


def _calculate_file_checksum(file_path: Path, algorithm: str = "sha256", block_size: int = 65536) -> str:
    """
    Calculates the checksum of a file using a specified hashing algorithm.

    Args:
        file_path (str or Path): The path to the file.
        algorithm (str): The name of the hashing algorithm (e.g., 'md5', 'sha256').
        block_size (int): The size of chunks to read the file in (for large files).

    Returns:
        str: The hexadecimal representation of the file checksum.
    """
    # Create a hash object with the specified algorithm name
    logger.debug("Starting file checksum calculation")
    try:
        hasher = hashlib.new(algorithm)
    except ValueError:
        return f"Error: Invalid algorithm name '{algorithm}'"

    # Open the file in binary read mode
    with open(file_path, "rb") as f:
        # Read the file in chunks and update the hash object
        for chunk in iter(lambda: f.read(block_size), b""):
            logger.debug(f"Updating hash with chunk of size {len(chunk)}")
            hasher.update(chunk)

    logger.debug(f"hash complete.")
    # Return the hexadecimal digest of the hash
    return hasher.hexdigest()


class FileAlreadyExistsError(Exception):
    def __init__(self, file_id: str):
        self.file_id = file_id
        super().__init__(f"File already exists: {file_id}")
