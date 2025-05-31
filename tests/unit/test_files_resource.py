import json
from pathlib import Path

from httpx import (
    Response,
)
from pytest_mock import MockerFixture

from together import Together
from together.types import (
    FileRetrieveResponse,
)


def test_file_upload_file(mocker: MockerFixture, tmp_path: Path):
    # Mock the API requestor

    content = [{"text": "Hello, world!"}, {"text": "How are you?"}]
    content_str = "\n".join(json.dumps(item) for item in content)
    content_bytes = content_str.encode()

    mock_request = mocker.MagicMock()
    mock_request.headers = {}  # response.request headers have to be set otherwise it will confuse the framework and not parse the response into an object

    mock_send_response0 = Response(
        status_code=302,
        headers={
            "Location": "https://3721873h1.r2.cloudflarestorage.com/together-dev//finetune/file-30b2f515-c146-4780-80e6-d8a84f4caaaa",
            "X-Together-File-Id": "file-30b2f515-c146-4780-80e6-d8a84f4caaaa",
        },
        request=mock_request,
    )
    mock_put_response0 = Response(
        status_code=200,
        request=mock_request,
    )
    mock_send_response1 = Response(
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
    mock_send_requestor.side_effect = [mock_send_response0, mock_send_response1]

    mock_put_requestor = mocker.MagicMock()
    mock_put_requestor.side_effect = [mock_put_response0]

    # Mock the post method directly on the client
    client = Together(api_key="fake_api_key")
    mocker.patch.object(client._client, "send", mock_send_requestor)
    mocker.patch.object(client._client, "put", mock_put_requestor)
    files = client.files

    # Make a temporary file object
    file = tmp_path / "valid.jsonl"
    with file.open("w") as f:
        f.write(content_str)

    # Test run method
    response = files.upload_file(
        file,
        purpose="fine-tune",
    )

    # Verify the response
    assert isinstance(response, FileRetrieveResponse)
    assert response.filename == "valid.jsonl"
    assert response.bytes == len(content_bytes)
    assert response.created_at == 1234567890
    assert response.file_type == "jsonl"
    assert response.line_count == 0
    assert response.object == "file"
    assert response.processed == True
    assert response.purpose == "fine-tune"
