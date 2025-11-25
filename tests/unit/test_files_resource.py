import json
from pathlib import Path

from httpx import (
    Response,
)
from pytest_mock import MockerFixture

from together import Together
from together.types import (
    FileResponse,
)


def test_file_upload(mocker: MockerFixture, tmp_path: Path):
    # Mock the API requestor

    content = [{"text": "Hello, world!"}, {"text": "How are you?"}]
    content_str = "\n".join(json.dumps(item) for item in content)
    content_bytes = content_str.encode()

    mock_request = mocker.MagicMock()
    mock_request.headers = {}  # response.request headers have to be set otherwise it will confuse the framework and not parse the response into an object

    # Mock response 1: POST /files (get presigned URL)
    mock_presigned_response = Response(
        status_code=302,
        headers={
            "Location": "https://mock-presigned-url.com",
            "X-Together-File-Id": "file-30b2f515-c146-4780-80e6-d8a84f4caaaa",
        },
        request=mock_request,
    )

    # Mock response 2: PUT to presigned URL (upload file)
    mock_upload_response = Response(
        status_code=200,
        request=mock_request,
    )

    # Mock response 3: POST /files/{file_id}/preprocess (finalize)
    mock_finalize_response = Response(
        status_code=200,
        json={
            "id": "file-30b2f515-c146-4780-80e6-d8a84f4caaaa",
            "bytes": len(content_str),
            "created_at": 1234567890,
            "filename": "valid.jsonl",
            "FileType": "jsonl",
            "LineCount": 0,
            "purpose": "fine-tune",
            "object": "file",
            "Processed": True,
        },
        request=mock_request,
    )

    mock_send_requestor = mocker.MagicMock()
    mock_send_requestor.side_effect = [mock_presigned_response, mock_upload_response, mock_finalize_response]

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
    assert response.line_count == 0
    assert response.object == "file"
    assert response.processed == True
    assert response.purpose == "fine-tune"
