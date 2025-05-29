from __future__ import annotations

import os
import stat
import uuid
import shutil
import tempfile
from typing import Tuple
from pathlib import Path
from functools import partial

import httpx
from tqdm import tqdm
from filelock import FileLock
from tqdm.utils import CallbackIOWrapper

from ...types import FileType, FilePurpose, FileRetrieveResponse
from ..._types import RequestOptions
from ..constants import DISABLE_TQDM, DOWNLOAD_BLOCK_SIZE
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..types.error import DownloadError, FileTypeError
from ..._exceptions import APIStatusError, AuthenticationError


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

    assert remote_name, "No model name found in fine_tune object. Please specify an `output` file name."

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
                    os.remove(lock_path)
                    raise APIStatusError(
                        "Error downloading file",
                        response=e.response,
                        body=e.response,
                    ) from e

                if not fetch_metadata:
                    file_size = int(response.headers.get("content-length", 0))

                assert file_size != 0, "Unable to retrieve remote file."

                with tqdm(
                    total=file_size,
                    unit="B",
                    unit_scale=True,
                    desc=f"Downloading file {file_path.name}",
                    disable=bool(DISABLE_TQDM),
                ) as pbar:
                    for chunk in response.iter_bytes(DOWNLOAD_BLOCK_SIZE):
                        pbar.update(len(chunk))
                        temp_file.write(chunk)  # type: ignore

            # Raise exception if remote file size does not match downloaded file size
            if os.stat(temp_file.name).st_size != file_size:
                DownloadError(
                    f"Downloaded file size `{pbar.n}` bytes does not match remote file size `{file_size}` bytes."
                )

            # Moves temp file to output file path
            chmod_and_replace(Path(temp_file.name), file_path)

        os.remove(lock_path)

        return str(file_path.resolve()), file_size


class UploadManager(SyncAPIResource):
    def get_upload_url(
        self,
        url: str,
        file: Path,
        purpose: FilePurpose,
        filetype: FileType,
    ) -> Tuple[str, str]:
        data = {
            "purpose": purpose,
            "file_name": file.name,
            "file_type": filetype,
        }

        try:
            response = self._client.post(
                path=url,
                cast_to=httpx.Response,
                body=data,
            )
        except APIStatusError as e:
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
                )
            response = e.response

        redirect_url = response.headers["Location"]
        file_id = response.headers["X-Together-File-Id"]

        return redirect_url, file_id

    def callback(self, url: str) -> FileRetrieveResponse:
        response = self._client.post(
            cast_to=FileRetrieveResponse,
            path=url,
        )

        return response

    def upload(
        self,
        url: str,
        file: Path,
        purpose: FilePurpose,
        redirect: bool = False,
    ) -> FileRetrieveResponse:
        file_id = None

        redirect_url = None
        if redirect:
            if file.suffix == ".jsonl":
                filetype = "jsonl"
            elif file.suffix == ".parquet":
                filetype = "parquet"
            else:
                raise FileTypeError(
                    f"Unknown extension of file {file}. Only files with extensions .jsonl and .parquet are supported."
                )
            redirect_url, file_id = self.get_upload_url(url, file, purpose, filetype)  # type: ignore

        file_size = os.stat(file.as_posix()).st_size

        with tqdm(
            total=file_size,
            unit="B",
            unit_scale=True,
            desc=f"Uploading file {file.name}",
            disable=bool(DISABLE_TQDM),
        ) as pbar:
            with file.open("rb") as f:
                wrapped_file = CallbackIOWrapper(pbar.update, f, "read")

                if redirect:
                    assert redirect_url is not None
                    callback_response = self._client.put(
                        cast_to=httpx.Response,
                        path=redirect_url,
                        body=wrapped_file,
                    )
                else:
                    response = self._client.put(
                        cast_to=FileRetrieveResponse,
                        path=url,
                        body=wrapped_file,
                    )

        if redirect:
            assert isinstance(callback_response, httpx.Response)  # type: ignore

            if not callback_response.status_code == 200:
                raise APIStatusError(
                    f"Error during file upload: {callback_response.content.decode()}, headers: {callback_response.headers}",
                    response=callback_response,
                    body=callback_response.content.decode(),
                )

            response = self.callback(f"{url}/{file_id}/preprocess")

        assert isinstance(response, FileRetrieveResponse)  # type: ignore

        return response


class AsyncUploadManager(AsyncAPIResource):
    async def get_upload_url(
        self,
        url: str,
        file: Path,
        purpose: FilePurpose,
        filetype: FileType,
    ) -> Tuple[str, str]:
        data = {
            "purpose": purpose,
            "file_name": file.name,
            "file_type": filetype,
        }

        try:
            response = await self._client.post(
                path=url,
                cast_to=httpx.Response,
                body=data,
            )
        except APIStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError(
                    "This job would exceed your free trial credits. "
                    "Please upgrade to a paid account through "
                    "Settings -> Billing on api.together.ai to continue.",
                    response=e.response,
                    body=e.body,
                ) from e
            raise

        # Raise error for non 302 status codes
        if response.status_code != 302:
            raise APIStatusError(
                f"Unexpected error raised by endpoint: {response.content.decode()}, headers: {response.headers}",
                response=response,
                body=response.content.decode(),
            )

        redirect_url = response.headers["Location"]
        file_id = response.headers["X-Together-File-Id"]

        return redirect_url, file_id

    async def callback(self, url: str) -> FileRetrieveResponse:
        response = self._client.post(
            cast_to=FileRetrieveResponse,
            path=url,
        )

        return await response

    async def upload(
        self,
        url: str,
        file: Path,
        purpose: FilePurpose,
        redirect: bool = False,
    ) -> FileRetrieveResponse:
        file_id = None

        redirect_url = None
        if redirect:
            if file.suffix == ".jsonl":
                filetype = "jsonl"
            elif file.suffix == ".parquet":
                filetype = "parquet"
            else:
                raise FileTypeError(
                    f"Unknown extension of file {file}. Only files with extensions .jsonl and .parquet are supported."
                )
            redirect_url, file_id = await self.get_upload_url(url, file, purpose, filetype)  # type: ignore

        file_size = os.stat(file.as_posix()).st_size

        with tqdm(
            total=file_size,
            unit="B",
            unit_scale=True,
            desc=f"Uploading file {file.name}",
            disable=bool(DISABLE_TQDM),
        ) as pbar:
            with file.open("rb") as f:
                wrapped_file = CallbackIOWrapper(pbar.update, f, "read")

                if redirect:
                    assert redirect_url is not None
                    callback_response = self._client.put(
                        cast_to=httpx.Response,
                        path=redirect_url,
                        body=wrapped_file,
                    )
                else:
                    response = self._client.put(
                        cast_to=FileRetrieveResponse,
                        path=url,
                        body=wrapped_file,
                    )

        if redirect:
            assert isinstance(callback_response, httpx.Response)  # type: ignore

            if not callback_response.status_code == 200:
                raise APIStatusError(
                    f"Error during file upload: {callback_response.content.decode()}, headers: {callback_response.headers}",
                    response=callback_response,
                    body=callback_response.content.decode(),
                )

            response = self.callback(f"{url}/{file_id}/preprocess")

        assert isinstance(response, FileRetrieveResponse)  # type: ignore

        return response
