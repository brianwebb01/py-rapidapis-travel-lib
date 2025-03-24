import pytest
from unittest.mock import patch, MagicMock
from rapid_bookingcom.services.client import BookingAPIClient
import requests

@pytest.fixture
def client():
    return BookingAPIClient()

def test_client_initialization(client):
    """Test that the client is initialized with correct attributes"""
    assert client.api_key is not None
    assert client.api_host is not None
    assert client.base_url == f"https://{client.api_host}/api/v1"
    assert client.headers == {
        "x-rapidapi-key": client.api_key,
        "x-rapidapi-host": client.api_host
    }

def test_make_request_success(client):
    """Test successful API request"""
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "success"}
    mock_response.raise_for_status.return_value = None

    with patch('requests.request') as mock_request:
        mock_request.return_value = mock_response

        response = client._make_request(
            endpoint="/test",
            method="GET",
            params={"key": "value"}
        )

        # Verify request was made with correct parameters
        mock_request.assert_called_once()
        call_args = mock_request.call_args[1]
        assert call_args['method'] == "GET"
        assert call_args['url'] == f"{client.base_url}/test"
        assert call_args['headers'] == client.headers
        assert call_args['params'] == {"key": "value"}
        assert call_args['json'] is None

        # Verify response
        assert response == {"data": "success"}

def test_make_request_with_json_data(client):
    """Test API request with JSON data"""
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "success"}
    mock_response.raise_for_status.return_value = None

    with patch('requests.request') as mock_request:
        mock_request.return_value = mock_response

        json_data = {"key": "value"}
        response = client._make_request(
            endpoint="/test",
            method="POST",
            data=json_data
        )

        # Verify request was made with correct parameters
        mock_request.assert_called_once()
        call_args = mock_request.call_args[1]
        assert call_args['method'] == "POST"
        assert call_args['url'] == f"{client.base_url}/test"
        assert call_args['headers'] == client.headers
        assert call_args['json'] == json_data
        assert call_args['params'] is None

        # Verify response
        assert response == {"data": "success"}

def test_make_request_http_error(client):
    """Test API request with HTTP error"""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("HTTP Error")

    with patch('requests.request') as mock_request:
        mock_request.return_value = mock_response

        with pytest.raises(requests.exceptions.RequestException) as exc_info:
            client._make_request(endpoint="/test")

        assert str(exc_info.value) == "API request failed: HTTP Error"

def test_make_request_invalid_json(client):
    """Test API request with invalid JSON response"""
    mock_response = MagicMock()
    mock_response.json.side_effect = ValueError("Invalid JSON")

    with patch('requests.request') as mock_request:
        mock_request.return_value = mock_response

        with pytest.raises(ValueError) as exc_info:
            client._make_request(endpoint="/test")

        assert str(exc_info.value) == "Invalid JSON response: Invalid JSON"