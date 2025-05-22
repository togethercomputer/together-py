import json

import pytest
from httpx import (
    URL,
    Request,
    Response,
)
from pytest_mock import MockerFixture

from together import Together
from together._compat import parse_obj
from together.types.execute_response import (
    SuccessfulExecution,
    SuccessfulExecutionData,
    SuccessfulExecutionDataOutputError,
    SuccessfulExecutionDataOutputStreamOutput,
    SuccessfulExecutionDataOutputDisplayorExecuteOutput,
    SuccessfulExecutionDataOutputDisplayorExecuteOutputData,
)
from together.resources.code_interpreter import CodeInterpreterResource
from together.types.code_interpreter_execute_params import (
    File,
)


def test_interpreter_output_validation():
    # Test stdout output
    stdout = SuccessfulExecutionDataOutputStreamOutput(type="stdout", data="Hello, world!")
    assert stdout.type == "stdout"
    assert stdout.data == "Hello, world!"

    # Test stderr output
    stderr = SuccessfulExecutionDataOutputStreamOutput(type="stderr", data="Warning message")
    assert stderr.type == "stderr"
    assert stderr.data == "Warning message"

    # Test error output
    error = SuccessfulExecutionDataOutputError(type="error", data="Error occurred")
    assert error.type == "error"
    assert error.data == "Error occurred"

    # Test display_data output with dict data
    display_data = SuccessfulExecutionDataOutputDisplayorExecuteOutput(
        type="display_data",
        data=parse_obj(
            SuccessfulExecutionDataOutputDisplayorExecuteOutputData,
            {
                "text/plain": "Hello",
                "text/html": "<p>Hello</p>",
            },
        ),
    )
    assert display_data.type == "display_data"
    assert isinstance(display_data.data, SuccessfulExecutionDataOutputDisplayorExecuteOutputData)
    assert display_data.data.text_plain == "Hello"
    assert display_data.data.text_html == "<p>Hello</p>"

    # Test execute_result output
    execute_result = SuccessfulExecutionDataOutputDisplayorExecuteOutput(
        type="execute_result",
        data=parse_obj(
            SuccessfulExecutionDataOutputDisplayorExecuteOutputData,
            {
                "text/plain": "42",
            },
        ),
    )
    assert execute_result.type == "execute_result"
    assert execute_result.data.text_plain == "42"


def test_execute_response_validation():
    # Test valid response
    outputs = [
        SuccessfulExecutionDataOutputStreamOutput(type="stdout", data="Hello"),
        SuccessfulExecutionDataOutputStreamOutput(type="stderr", data="Warning"),
    ]
    response = SuccessfulExecution(
        data=SuccessfulExecutionData(
            session_id="test_session",
            status="success",
            outputs=outputs,  # type: ignore
        )
    )
    assert response.data.session_id == "test_session"
    assert response.data.status == "success"
    assert len(response.data.outputs) == 2
    assert response.data.outputs[0].type == "stdout"
    assert response.data.outputs[1].type == "stderr"


def test_code_interpreter_run(mocker: MockerFixture):
    # Mock the API requestor
    response_data = {
        "data": {
            "session_id": "test_session",
            "status": "success",
            "outputs": [{"type": "stdout", "data": "Hello, world!"}],
        }
    }
    mock_headers = {
        "cf-ray": "test-ray-id-files",
        "x-ratelimit-remaining": "98",
        "x-hostname": "test-host",
        "x-total-time": "42.0",
    }
    mock_request = mocker.MagicMock()
    mock_request.headers = {}
    mock_response = Response(status_code=200, json=response_data, headers=mock_headers, request=mock_request)
    mock_requestor = mocker.MagicMock()
    mock_requestor.return_value = mock_response

    # Mock the post method directly on the client
    client = Together(api_key="fake_api_key")
    mocker.patch.object(client._client, "send", mock_requestor)
    interpreter = CodeInterpreterResource(client)

    # Test run method
    response = interpreter.execute(
        code='print("Hello, world!")',
        language="python",
        session_id="test_session",
    )

    # Verify the response
    assert isinstance(response, SuccessfulExecution)
    assert response.data is not None
    assert response.data.session_id == "test_session"
    assert response.data.status == "success"
    assert len(response.data.outputs) == 1
    assert response.data.outputs[0].type == "stdout"
    assert response.data.outputs[0].data == "Hello, world!"

    # Verify API request
    mock_requestor.assert_called_once_with(
        mocker.ANY,
        stream=False,
    )
    request = mock_requestor.call_args[0][0]
    assert isinstance(request, Request)
    assert request.method == "POST"
    assert request.url == URL("https://api.together.xyz/v1/tci/execute")
    assert json.loads(request.read().decode()) == {
        "code": 'print("Hello, world!")',
        "language": "python",
        "session_id": "test_session",
    }


def test_code_interpreter_run_without_session(mocker: MockerFixture):
    # Mock the API requestor
    response_data = {  # type: ignore
        "data": {
            "session_id": "new_session",
            "status": "success",
            "outputs": [],
        }
    }
    mock_headers = {
        "cf-ray": "test-ray-id-files",
        "x-ratelimit-remaining": "98",
        "x-hostname": "test-host",
        "x-total-time": "42.0",
    }
    mock_request = mocker.MagicMock()
    mock_request.headers = {}
    mock_response = Response(status_code=200, json=response_data, headers=mock_headers, request=mock_request)
    mock_requestor = mocker.MagicMock()
    mock_requestor.return_value = mock_response

    # Mock the post method directly on the client
    client = Together(api_key="fake_api_key")
    mocker.patch.object(client._client, "send", mock_requestor)
    interpreter = CodeInterpreterResource(client)

    # Test run method without session_id
    response = interpreter.execute(
        code="x = 1",
        language="python",
    )

    # Verify the response
    assert isinstance(response, SuccessfulExecution)
    assert response.data is not None
    assert response.data.session_id == "new_session"


def test_code_interpreter_error_handling(mocker: MockerFixture):
    # Mock the API requestor to simulate an error
    response_data = {
        "data": {
            "session_id": "test_session",
            "status": "error",
            "outputs": [{"type": "error", "data": "Division by zero"}],
        }
    }
    mock_headers = {
        "cf-ray": "test-ray-id-files",
        "x-ratelimit-remaining": "98",
        "x-hostname": "test-host",
        "x-total-time": "42.0",
    }
    mock_request = mocker.MagicMock()
    mock_request.headers = {}
    mock_response = Response(status_code=200, json=response_data, headers=mock_headers, request=mock_request)
    mock_requestor = mocker.MagicMock()
    mock_requestor.return_value = mock_response

    # Mock the post method directly on the client
    client = Together(api_key="fake_api_key")
    mocker.patch.object(client._client, "send", mock_requestor)
    interpreter = CodeInterpreterResource(client)

    # Test run method with code that would cause an error
    response = interpreter.execute(
        code="1/0",  # This will cause a division by zero error
        language="python",
        session_id="test_session",
    )

    # Verify the error response
    assert isinstance(response, SuccessfulExecution)
    assert response.data is not None
    assert response.data.status == "error"
    assert len(response.data.outputs) == 1
    assert response.data.outputs[0].type == "error"
    assert "Division by zero" in response.data.outputs[0].data


def test_code_interpreter_multiple_outputs(mocker: MockerFixture):
    # Mock the API requestor
    response_data = {
        "data": {
            "session_id": "test_session",
            "status": "success",
            "outputs": [
                {"type": "stdout", "data": "First line"},
                {"type": "stderr", "data": "Warning message"},
                {"type": "execute_result", "data": "42"},
            ],
        }
    }
    mock_headers = {
        "cf-ray": "test-ray-id-files",
        "x-ratelimit-remaining": "98",
        "x-hostname": "test-host",
        "x-total-time": "42.0",
    }
    mock_request = mocker.MagicMock()
    mock_request.headers = {}
    mock_response = Response(status_code=200, json=response_data, headers=mock_headers, request=mock_request)
    mock_requestor = mocker.MagicMock()
    mock_requestor.return_value = mock_response

    # Mock the post method directly on the client
    client = Together(api_key="fake_api_key")
    mocker.patch.object(client._client, "send", mock_requestor)
    interpreter = CodeInterpreterResource(client)

    # Test run method with code that produces multiple outputs
    response = interpreter.execute(
        code='print("First line")\nimport sys\nsys.stderr.write("Warning message")\n42',
        language="python",
        session_id="test_session",
    )

    # Verify the response with multiple outputs
    assert isinstance(response, SuccessfulExecution)
    assert response.data is not None
    assert response.data.status == "success"
    assert len(response.data.outputs) == 3
    assert response.data.outputs[0].type == "stdout"
    assert response.data.outputs[1].type == "stderr"
    assert response.data.outputs[2].type == "execute_result"


def test_code_interpreter_session_management(mocker: MockerFixture):
    # First response - create new session
    response_data1 = {
        "data": {
            "session_id": "new_session",
            "status": "success",
            "outputs": [{"type": "stdout", "data": "First execution"}],
        }
    }

    # Second response - use existing session
    response_data2 = {
        "data": {
            "session_id": "new_session",
            "status": "success",
            "outputs": [{"type": "stdout", "data": "Second execution"}],
        }
    }

    mock_headers = {
        "cf-ray": "test-ray-id-files",
        "x-ratelimit-remaining": "98",
        "x-hostname": "test-host",
        "x-total-time": "42.0",
    }
    mock_request = mocker.MagicMock()
    mock_request.headers = {}
    mock_response1 = Response(status_code=200, json=response_data1, headers=mock_headers, request=mock_request)
    mock_response2 = Response(status_code=200, json=response_data2, headers=mock_headers, request=mock_request)
    # Mock the post method directly on the client
    client = Together(api_key="fake_api_key")
    mock_requestor = mocker.MagicMock()
    mock_requestor.side_effect = [
        mock_response1,
        mock_response2,
    ]
    # The mock_requestor becomes the mock for client._client.send
    mocker.patch.object(client._client, "send", mock_requestor)
    # Now mock_requestor can be used to track calls

    interpreter = CodeInterpreterResource(client)

    # First execution - no session ID
    response1 = interpreter.execute(
        code='print("First execution")',
        language="python",
    )

    # Second execution - using session ID from first execution
    assert response1.data is not None
    response2 = interpreter.execute(
        code='print("Second execution")',
        language="python",
        session_id=response1.data.session_id,
    )

    # Verify both responses
    assert response1.data is not None
    assert response2.data is not None
    assert response1.data.session_id == "new_session"
    assert response2.data.session_id == "new_session"
    assert len(response1.data.outputs) == 1
    assert len(response2.data.outputs) == 1
    assert response1.data.outputs[0].data == "First execution"
    assert response2.data.outputs[0].data == "Second execution"

    # Verify API calls
    assert mock_requestor.call_count == 2
    calls = mock_requestor.call_args_list

    # First call should not have session_id
    request1 = calls[0][0][0]
    assert isinstance(request1, Request)
    assert "session_id" not in json.loads(request1.read().decode())

    # Second call should have session_id
    request2 = calls[1][0][0]
    assert isinstance(request2, Request)
    assert json.loads(request2.read().decode())["session_id"] == "new_session"


def test_code_interpreter_run_with_files(mocker: MockerFixture):
    mock_requestor = mocker.MagicMock()
    response_data = {
        "data": {
            "session_id": "test_session_files",
            "status": "success",
            "outputs": [{"type": "stdout", "data": "File content read"}],
        }
    }
    mock_headers = {
        "cf-ray": "test-ray-id-files",
        "x-ratelimit-remaining": "98",
        "x-hostname": "test-host",
        "x-total-time": "42.0",
    }
    mock_request = mocker.MagicMock()
    mock_request.headers = {}
    mock_response = Response(status_code=200, json=response_data, headers=mock_headers, request=mock_request)
    mock_requestor = mocker.MagicMock()
    mock_requestor.return_value = mock_response

    # Mock the post method directly on the client
    client = Together(api_key="fake_api_key")
    mocker.patch.object(client._client, "send", mock_requestor)
    interpreter = CodeInterpreterResource(client)

    # Define files
    files_to_upload = [
        File({"name": "test.txt", "encoding": "string", "content": "Hello from file!"}),
        File({"name": "image.png", "encoding": "base64", "content": "aW1hZ2UgZGF0YQ=="}),
    ]

    # Test run method with files (passing list of dicts)
    response = interpreter.execute(
        code='with open("test.txt") as f: print(f.read())',
        language="python",
        files=files_to_upload,  # Pass the list of dictionaries directly
    )

    # Verify the response
    assert isinstance(response, SuccessfulExecution)
    assert response.data is not None
    assert response.data.session_id == "test_session_files"
    assert response.data.status == "success"
    assert len(response.data.outputs) == 1
    assert response.data.outputs[0].type == "stdout"

    # Verify API request includes files (expected_files_payload remains the same)
    mock_requestor.assert_called_once_with(
        mocker.ANY,
        stream=False,
    )
    request = mock_requestor.call_args[0][0]
    assert isinstance(request, Request)
    assert request.method == "POST"
    assert request.url == URL("https://api.together.xyz/v1/tci/execute")
    expected_files_payload = [
        {"name": "test.txt", "encoding": "string", "content": "Hello from file!"},
        {"name": "image.png", "encoding": "base64", "content": "aW1hZ2UgZGF0YQ=="},
    ]
    assert json.loads(request.read().decode()) == {
        "code": 'with open("test.txt") as f: print(f.read())',
        "language": "python",
        "files": expected_files_payload,
    }


@pytest.mark.skip(
    "Skipping tests around raising an error on a bad file dict structure.  This is handled with pyright type hinting."
)
def test_code_interpreter_run_with_invalid_file_dict_structure(mocker: MockerFixture):
    """Test that run raises ValueError for missing keys in file dict."""
    client = mocker.MagicMock()
    interpreter = CodeInterpreterResource(client)

    with pytest.raises(ValueError, match="Invalid file input format"):
        invalid_files = [
            File({"name": "test.txt", "content": "Missing encoding"})  # type: ignore Missing 'encoding'
        ]

        interpreter.execute(
            code="print('test')",
            language="python",
            files=invalid_files,
        )


@pytest.mark.skip(
    "Skipping tests around raising an error on a bad file dict structure.  This is handled with pyright type hinting."
)
def test_code_interpreter_run_with_invalid_file_dict_encoding(mocker: MockerFixture):
    """Test that run raises ValueError for invalid encoding value."""
    client = mocker.MagicMock()
    interpreter = CodeInterpreterResource(client)

    with pytest.raises(ValueError, match="Invalid file input format"):
        invalid_files = [
            File(
                {
                    "name": "test.txt",
                    "encoding": "utf-8",  # type: ignore Invalid 'encoding' value
                    "content": "Invalid encoding",
                }
            )
        ]

        interpreter.execute(
            code="print('test')",
            language="python",
            files=invalid_files,
        )


def test_code_interpreter_run_with_invalid_file_list_item(mocker: MockerFixture):
    """Test that run raises ValueError for non-dict item in files list."""
    client = mocker.MagicMock()
    interpreter = CodeInterpreterResource(client)

    with pytest.raises(
        ValueError,
        match="dictionary update sequence element #0 has length 1; 2 is required",
    ):
        invalid_files = [
            File({"name": "good.txt", "encoding": "string", "content": "Good"}),
            File("not a dictionary"),  # type: ignore Invalid item type
        ]

        interpreter.execute(
            code="print('test')",
            language="python",
            files=invalid_files,
        )
