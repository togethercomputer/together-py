import json
from pathlib import Path

from httpx import (
    Request,
    Response,
    SyncByteStream,
)
from pytest_mock import MockerFixture

from together import Together
from together.types import (
    FileResponse,
)
from together.lib.resources.files import FileUploadProgress


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
