import pytest
from datetime import timedelta
import time
from pathlib import Path
from src.utils.cache import cache_sec_response, clear_cache
from src.config import settings

# Test function to simulate API calls
@cache_sec_response()
def mock_api_call(param: str):
    """Mock API call that returns different timestamps"""
    return {"timestamp": time.time(), "param": param}

@cache_sec_response(expires_after=timedelta(seconds=1))
def mock_expiring_api_call(param: str):
    """Mock API call with expiring cache"""
    return {"timestamp": time.time(), "param": param}

def test_cache_creation():
    """Test that cache files are created"""
    clear_cache()  # Start with clean cache
    result1 = mock_api_call("test")
    
    # Check that cache directory exists and contains a file
    cache_files = list(settings.CACHE_DIR.glob("*.json"))
    assert len(cache_files) == 1

def test_cache_hit():
    """Test that cached responses are returned"""
    clear_cache()
    
    # Make two identical calls
    result1 = mock_api_call("test")
    result2 = mock_api_call("test")
    
    # Should return same timestamp
    assert result1["timestamp"] == result2["timestamp"]

def test_cache_miss():
    """Test that different parameters create different caches"""
    clear_cache()
    
    # Make calls with different parameters
    result1 = mock_api_call("test1")
    result2 = mock_api_call("test2")
    
    # Should return different timestamps
    assert result1["timestamp"] != result2["timestamp"]

def test_cache_expiration():
    """Test that cache expires correctly"""
    clear_cache()
    
    # Make initial call
    result1 = mock_expiring_api_call("test")
    
    # Wait for cache to expire
    time.sleep(1.1)
    
    # Make second call
    result2 = mock_expiring_api_call("test")
    
    # Should return different timestamps
    assert result1["timestamp"] != result2["timestamp"]

def test_clear_cache():
    """Test cache clearing functionality"""
    # Create some cache entries
    mock_api_call("test1")
    mock_api_call("test2")
    
    # Clear cache
    count = clear_cache()
    assert count > 0
    
    # Check that cache directory is empty
    cache_files = list(settings.CACHE_DIR.glob("*.json"))
    assert len(cache_files) == 0

def test_clear_cache_pattern():
    """Test selective cache clearing"""
    clear_cache()
    
    # Create cache entries with different parameters
    mock_api_call("test1")
    mock_api_call("another")
    
    # Clear only 'test' caches
    count = clear_cache(pattern="test")
    assert count == 1
    
    # Check remaining cache files
    cache_files = list(settings.CACHE_DIR.glob("*.json"))
    assert len(cache_files) == 1