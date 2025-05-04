import pytest
from datetime import timedelta
import time
from src.utils.sec_client import SECClient, SECRateLimitError, SECDataError
from src.utils.cache import clear_cache
from unittest.mock import patch, MagicMock

@pytest.fixture
def sec_client():
    return SECClient()

@pytest.fixture(autouse=True)
def clear_test_cache():
    """Clear cache before each test"""
    clear_cache()
    yield
    clear_cache()

def test_validate_cik():
    client = SECClient()
    assert client._validate_cik("28917") == "0000028917"
    assert client._validate_cik("0000028917") == "0000028917"
    
    with pytest.raises(ValueError):
        client._validate_cik("invalid")

@patch('requests.request')
def test_rate_limiting(mock_request, sec_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"test": "data"}
    mock_request.return_value = mock_response
    
    # Make multiple requests and verify rate limiting
    for _ in range(3):
        result = sec_client._make_request("http://test.url")
        assert result == {"test": "data"}
    
    assert mock_request.call_count == 3

@patch('requests.request')
def test_rate_limit_error_handling(mock_request, sec_client):
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_request.return_value = mock_response
    
    with pytest.raises(SECRateLimitError):
        sec_client._make_request("http://test.url")

@patch('requests.request')
def test_get_company_submissions_with_cache(mock_request, sec_client):
    """Test that company submissions are cached"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "cik": "0000028917",
        "name": "Test Company",
        "tickers": ["TEST"]
    }
    mock_request.return_value = mock_response
    
    # First call should hit the API
    result1 = sec_client.get_company_submissions("28917")
    assert result1["cik"] == "0000028917"
    assert mock_request.call_count == 1
    
    # Second call should use cache
    result2 = sec_client.get_company_submissions("28917")
    assert result2["cik"] == "0000028917"
    assert mock_request.call_count == 1  # Count shouldn't increase

@patch('requests.request')
def test_get_company_facts_with_cache(mock_request, sec_client):
    """Test that company facts are cached"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "cik": "0000028917",
        "facts": {"us-gaap": {}}
    }
    mock_request.return_value = mock_response
    
    # First call should hit the API
    result1 = sec_client.get_company_facts("28917")
    assert mock_request.call_count == 1
    
    # Second call should use cache
    result2 = sec_client.get_company_facts("28917")
    assert mock_request.call_count == 1

@patch('requests.request')
def test_get_frames_with_cache(mock_request, sec_client):
    """Test that frames data is cached"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "taxonomy": "us-gaap",
        "tag": "Assets",
        "data": []
    }
    mock_request.return_value = mock_response
    
    # First call should hit the API
    result1 = sec_client.get_frames(
        taxonomy="us-gaap",
        tag="Assets",
        unit="USD",
        year=2024
    )
    assert mock_request.call_count == 1
    
    # Second call should use cache
    result2 = sec_client.get_frames(
        taxonomy="us-gaap",
        tag="Assets",
        unit="USD",
        year=2024
    )
    assert mock_request.call_count == 1

def test_invalid_quarter():
    client = SECClient()
    with pytest.raises(ValueError):
        client.get_frames(
            taxonomy="us-gaap",
            tag="Assets",
            unit="USD",
            year=2024,
            quarter=5
        )