from __future__ import annotations

import json
from typing import cast
from pathlib import Path

import httpx
import pytest
from httpx import (
    Request,
    Response,
    SyncByteStream,
    AsyncByteStream,
)
from respx import MockRouter
from pytest_mock import MockerFixture
from respx.models import Call

from together import Together, AsyncTogether
from together.types import (
    FileResponse,
)
from together._exceptions import APIStatusError
from together.lib.resources.files import (
    FileUploadProgress,
    _put_file_content,
    _aput_file_content,
    _validate_upload_file_id,
    _validate_upload_redirect_url,
)


def _mock_upload_responses(mocker: MockerFixture, *, content_str: str, filename: str = "valid.jsonl"):
    mock_request = mocker.MagicMock()
    mock_request.headers = {}  # response.request headers have to be set otherwise it will confuse the framework and not parse the response into an object

    mock_presigned_response = Response(
        status_code=302,
        headers={
            "Location": "https://mock-presigned-url.com",
            "X-Together-File-Id": "file-30b2f515-c146-4780-80e6-d8a84f4caaaa",
        },
        request=mock_request,
    )
    mock_upload_response = Response(
        status_code=200,
        request=mock_request,
    )
    mock_finalize_response = Response(
        status_code=200,
        json={
            "id": "file-30b2f515-c146-4780-80e6-d8a84f4caaaa",
            "bytes": len(content_str),
            "created_at": 1234567890,
            "filename": filename,
            "FileType": "jsonl",
            "purpose": "fine-tune",
            "object": "file",
            "Processed": True,
        },
        request=mock_request,
    )
    return [mock_presigned_response, mock_upload_response, mock_finalize_response]


def test_file_upload(mocker: MockerFixture, tmp_path: Path):
    # Mock the API requestor

    content = [{"text": "Hello, world!"}, {"text": "How are you?"}]
    content_str = "\n".join(json.dumps(item) for item in content)
    content_bytes = content_str.encode()

    mock_send_requestor = mocker.MagicMock()
    mock_send_requestor.side_effect = _mock_upload_responses(mocker, content_str=content_str)

    # Mock the post method directly on the client
    client = Together(api_key="fake_api_key")
    mocker.patch.object(client._client, "send", mock_send_requestor)
    files = client.files

    # Make a temporary file object
    file = tmp_path / "valid.jsonl"
    with file.open("w") as f:
        f.write(content_str)

    # Test run method
    response = files.upload(
        file,
        purpose="fine-tune",
    )

    # Verify the response
    assert isinstance(response, FileResponse)
    assert response.filename == "valid.jsonl"
    assert response.bytes == len(content_bytes)
    assert response.created_at == 1234567890
    assert response.file_type == "jsonl"
    assert response.object == "file"
    assert response.processed == True
    assert response.purpose == "fine-tune"


@pytest.mark.parametrize(
    ("url", "should_pass"),
    [
        ("https://bucket.s3.us-west-2.amazonaws.com/key", True),
        ("https://mock-presigned-url.com/upload", True),
        ("http://bucket.s3.amazonaws.com/key", False),
        ("https://127.0.0.1/upload", False),
        ("https://localhost/upload", False),
        ("https://10.0.0.5/upload", False),
    ],
)
def test_validate_upload_redirect_url(url: str, should_pass: bool):
    if should_pass:
        assert _validate_upload_redirect_url(url) == url
    else:
        with pytest.raises(ValueError):
            _validate_upload_redirect_url(url)


def test_validate_upload_file_id():
    assert _validate_upload_file_id("file-30b2f515-c146-4780-80e6-d8a84f4caaaa").startswith("file-")
    with pytest.raises(ValueError):
        _validate_upload_file_id("../evil")
    with pytest.raises(ValueError):
        _validate_upload_file_id("file?x=1")


def test_file_upload_reports_progress_callback(mocker: MockerFixture, tmp_path: Path):
    content_str = json.dumps({"text": "Hello, world!"}) + "\n"
    responses = _mock_upload_responses(mocker, content_str=content_str)

    def send_and_consume(request: Request, *args: object, **kwargs: object) -> Response:  # noqa: ARG001
        # Consume streamed upload bodies so progress callbacks fire under the mock.
        stream = request.stream
        if isinstance(stream, SyncByteStream):
            for _chunk in stream:
                pass
            stream.close()
        return responses.pop(0)

    client = Together(api_key="fake_api_key")
    mocker.patch.object(client._client, "send", side_effect=send_and_consume)

    file = tmp_path / "valid.jsonl"
    file.write_text(content_str)

    events: list[FileUploadProgress] = []
    response = client.files.upload(
        file,
        purpose="fine-tune",
        progress_callback=events.append,
    )

    assert isinstance(response, FileResponse)
    assert events
    assert events[0] == FileUploadProgress(uploaded_bytes=0, total_bytes=len(content_str.encode()))
    assert events[-1].uploaded_bytes == events[-1].total_bytes == len(content_str.encode())


async def test_async_file_upload_reports_progress_callback(mocker: MockerFixture, tmp_path: Path):
    content_str = json.dumps({"text": "Hello, world!"}) + "\n"
    responses = _mock_upload_responses(mocker, content_str=content_str)

    async def send_and_consume(request: Request, *args: object, **kwargs: object) -> Response:  # noqa: ARG001
        # Consume streamed upload bodies so progress callbacks fire under the mock.
        # Also asserts AsyncClient gets an AsyncByteStream (sync iterators raise RuntimeError).
        stream = request.stream
        if isinstance(stream, AsyncByteStream):
            async for _chunk in stream:
                pass
            await stream.aclose()
        else:
            raise AssertionError(f"Expected AsyncByteStream, got {type(stream)!r}")
        return responses.pop(0)

    client = AsyncTogether(api_key="fake_api_key")
    mocker.patch.object(client._client, "send", side_effect=send_and_consume)

    file = tmp_path / "valid.jsonl"
    file.write_text(content_str)

    events: list[FileUploadProgress] = []
    response = await client.files.upload(
        file,
        purpose="fine-tune",
        progress_callback=events.append,
    )

    assert isinstance(response, FileResponse)
    assert events
    assert events[0] == FileUploadProgress(uploaded_bytes=0, total_bytes=len(content_str.encode()))
    assert events[-1].uploaded_bytes == events[-1].total_bytes == len(content_str.encode())


def _finalize_json(content_str: str, filename: str = "valid.jsonl") -> dict[str, object]:
    return {
        "id": "file-30b2f515-c146-4780-80e6-d8a84f4caaaa",
        "bytes": len(content_str),
        "created_at": 1234567890,
        "filename": filename,
        "FileType": "jsonl",
        "purpose": "fine-tune",
        "object": "file",
        "Processed": True,
    }


@pytest.mark.respx
def test_put_file_content_replays_body_on_307(respx_mock: MockRouter, tmp_path: Path) -> None:
    file = tmp_path / "valid.jsonl"
    payload = b'{"text": "hello"}\n'
    file.write_bytes(payload)

    first = respx_mock.put("https://s3.amazonaws.com/upload").mock(
        return_value=httpx.Response(
            307,
            headers={"Location": "https://s3.us-west-2.amazonaws.com/upload"},
        )
    )
    second = respx_mock.put("https://s3.us-west-2.amazonaws.com/upload").mock(return_value=httpx.Response(200))

    with httpx.Client(follow_redirects=True) as client:
        response = _put_file_content(
            client,
            "https://s3.amazonaws.com/upload",
            file,
            file_size=len(payload),
        )

    assert response.status_code == 200
    assert first.call_count == 1
    assert second.call_count == 1
    first_request = cast(Call, first.calls[0]).request
    second_request = cast(Call, second.calls[0]).request
    assert first_request.content == payload
    assert second_request.content == payload
    assert first_request.headers["Content-Length"] == str(len(payload))
    assert second_request.headers["Content-Length"] == str(len(payload))


@pytest.mark.respx
async def test_aput_file_content_replays_body_on_307(respx_mock: MockRouter, tmp_path: Path) -> None:
    file = tmp_path / "valid.jsonl"
    payload = b'{"text": "hello"}\n'
    file.write_bytes(payload)

    first = respx_mock.put("https://s3.amazonaws.com/upload").mock(
        return_value=httpx.Response(
            307,
            headers={"Location": "https://s3.us-west-2.amazonaws.com/upload"},
        )
    )
    second = respx_mock.put("https://s3.us-west-2.amazonaws.com/upload").mock(return_value=httpx.Response(200))

    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await _aput_file_content(
            client,
            "https://s3.amazonaws.com/upload",
            file,
            file_size=len(payload),
        )

    assert response.status_code == 200
    assert first.call_count == 1
    assert second.call_count == 1
    assert cast(Call, first.calls[0]).request.content == payload
    assert cast(Call, second.calls[0]).request.content == payload


@pytest.mark.respx
def test_put_file_content_rejects_unsafe_redirect(respx_mock: MockRouter, tmp_path: Path) -> None:
    file = tmp_path / "valid.jsonl"
    payload = b'{"text": "hello"}\n'
    file.write_bytes(payload)

    respx_mock.put("https://s3.amazonaws.com/upload").mock(
        return_value=httpx.Response(307, headers={"Location": "https://127.0.0.1/steal"})
    )

    with httpx.Client(follow_redirects=True) as client:
        with pytest.raises(APIStatusError, match="non-public address"):
            _put_file_content(
                client,
                "https://s3.amazonaws.com/upload",
                file,
                file_size=len(payload),
            )


def test_file_upload_follows_storage_307(mocker: MockerFixture, tmp_path: Path) -> None:
    content_str = json.dumps({"text": "Hello, world!"}) + "\n"
    content_bytes = content_str.encode()
    mock_request = mocker.MagicMock()
    mock_request.headers = {}
    responses = [
        Response(
            status_code=302,
            headers={
                "Location": "https://s3.amazonaws.com/upload",
                "X-Together-File-Id": "file-30b2f515-c146-4780-80e6-d8a84f4caaaa",
            },
            request=mock_request,
        ),
        Response(
            status_code=307,
            headers={"Location": "https://s3.us-west-2.amazonaws.com/upload"},
            request=mock_request,
        ),
        Response(status_code=200, request=mock_request),
        Response(status_code=200, json=_finalize_json(content_str), request=mock_request),
    ]
    put_urls: list[str] = []
    put_bodies: list[bytes] = []
    put_follow_redirects: list[object] = []

    def send_and_consume(request: Request, *args: object, **kwargs: object) -> Response:  # noqa: ARG001
        stream = request.stream
        if request.method == "PUT":
            put_urls.append(str(request.url))
            put_follow_redirects.append(kwargs.get("follow_redirects"))
            chunks: list[bytes] = []
            if isinstance(stream, SyncByteStream):
                for chunk in stream:
                    chunks.append(chunk)
                stream.close()
            put_bodies.append(b"".join(chunks))
        return responses.pop(0)

    client = Together(api_key="fake_api_key")
    mocker.patch.object(client._client, "send", side_effect=send_and_consume)

    file = tmp_path / "valid.jsonl"
    file.write_text(content_str)

    response = client.files.upload(file, purpose="fine-tune")

    assert isinstance(response, FileResponse)
    assert put_urls == [
        "https://s3.amazonaws.com/upload",
        "https://s3.us-west-2.amazonaws.com/upload",
    ]
    assert put_bodies == [content_bytes, content_bytes]
    assert put_follow_redirects == [False, False]


async def test_async_file_upload_follows_storage_307(mocker: MockerFixture, tmp_path: Path) -> None:
    content_str = json.dumps({"text": "Hello, world!"}) + "\n"
    content_bytes = content_str.encode()
    mock_request = mocker.MagicMock()
    mock_request.headers = {}
    responses = [
        Response(
            status_code=302,
            headers={
                "Location": "https://s3.amazonaws.com/upload",
                "X-Together-File-Id": "file-30b2f515-c146-4780-80e6-d8a84f4caaaa",
            },
            request=mock_request,
        ),
        Response(
            status_code=307,
            headers={"Location": "https://s3.us-west-2.amazonaws.com/upload"},
            request=mock_request,
        ),
        Response(status_code=200, request=mock_request),
        Response(status_code=200, json=_finalize_json(content_str), request=mock_request),
    ]
    put_urls: list[str] = []
    put_bodies: list[bytes] = []

    async def send_and_consume(request: Request, *args: object, **kwargs: object) -> Response:  # noqa: ARG001
        stream = request.stream
        if request.method == "PUT":
            put_urls.append(str(request.url))
            assert kwargs.get("follow_redirects") is False
            chunks: list[bytes] = []
            if isinstance(stream, AsyncByteStream):
                async for chunk in stream:
                    chunks.append(chunk)
                await stream.aclose()
            else:
                raise AssertionError(f"Expected AsyncByteStream, got {type(stream)!r}")
            put_bodies.append(b"".join(chunks))
        return responses.pop(0)

    client = AsyncTogether(api_key="fake_api_key")
    mocker.patch.object(client._client, "send", side_effect=send_and_consume)

    file = tmp_path / "valid.jsonl"
    file.write_text(content_str)

    response = await client.files.upload(file, purpose="fine-tune")

    assert isinstance(response, FileResponse)
    assert put_urls == [
        "https://s3.amazonaws.com/upload",
        "https://s3.us-west-2.amazonaws.com/upload",
    ]
    assert put_bodies == [content_bytes, content_bytes]
