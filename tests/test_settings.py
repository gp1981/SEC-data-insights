import os
import pytest
from pathlib import Path
from src.config import settings

def test_default_settings():
    """Test default configuration values"""
    assert settings.SEC_API_BASE_URL == "https://data.sec.gov"
    assert settings.SEC_RATE_LIMIT_DELAY == 0.1
    assert settings.SEC_MAX_RETRIES == 3
    assert settings.DATABASE_URL == 'sqlite:///sec_filings.db'

def test_override_settings(monkeypatch):
    """Test overriding settings via environment variables"""
    # Set test environment variables
    test_vars = {
        'SEC_USER_AGENT': 'Test Agent',
        'SEC_RATE_LIMIT_DELAY': '0.2',
        'SEC_MAX_RETRIES': '5',
        'DATABASE_URL': 'sqlite:///test.db',
        'LOG_LEVEL': 'DEBUG'
    }
    
    for key, value in test_vars.items():
        monkeypatch.setenv(key, value)
    
    # Reload settings
    import importlib
    importlib.reload(settings)
    
    # Verify overridden values
    assert settings.SEC_USER_AGENT == 'Test Agent'
    assert settings.SEC_RATE_LIMIT_DELAY == 0.2
    assert settings.SEC_MAX_RETRIES == 5
    assert settings.DATABASE_URL == 'sqlite:///test.db'
    assert settings.LOG_LEVEL == 'DEBUG'

def test_output_directories():
    """Test that required directories are created"""
    assert settings.OUTPUT_DIR.exists()
    assert settings.CACHE_DIR.exists()

def test_invalid_rate_limit_delay(monkeypatch):
    """Test handling of invalid rate limit delay"""
    monkeypatch.setenv('SEC_RATE_LIMIT_DELAY', 'invalid')
    
    with pytest.raises(ValueError):
        import importlib
        importlib.reload(settings)