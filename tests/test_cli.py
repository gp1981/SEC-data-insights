import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from pathlib import Path
import logging
from src.cli import cli
from src.utils.sec_client import SECRateLimitError

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def mock_sec_client():
    """Mock SEC client for testing"""
    with patch('src.cli.SECClient') as mock:
        yield mock

@pytest.fixture(autouse=True)
def clean_logs():
    """Clean up log files before and after tests"""
    log_dir = Path('logs')
    if log_dir.exists():
        for f in log_dir.glob('sec_data_*.log'):
            f.unlink()
    log_dir.mkdir(exist_ok=True)
    yield
    for f in log_dir.glob('sec_data_*.log'):
        f.unlink()

def test_company_info_success(runner, mock_sec_client):
    """Test successful company info retrieval"""
    mock_instance = mock_sec_client.return_value
    mock_instance.get_company_submissions.return_value = {
        'name': "DILLARD'S, INC.",
        'cik': '0000028917',
        'tickers': ['DDS', 'DDT']
    }
    
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['company-info', '28917'])
        assert result.exit_code == 0
        assert "DILLARD'S, INC." in result.output

def test_company_info_rate_limit(runner, mock_sec_client):
    """Test rate limit error handling"""
    mock_instance = mock_sec_client.return_value
    mock_instance.get_company_submissions.side_effect = SECRateLimitError("Rate limit exceeded")
    
    result = runner.invoke(cli, ['company-info', '28917'], catch_exceptions=False)
    assert result.exit_code == 1
    assert "Rate limit exceeded" in result.output

def test_verbose_logging(runner, mock_sec_client):
    """Test verbose logging setup"""
    mock_instance = mock_sec_client.return_value
    mock_instance.get_company_submissions.return_value = {'name': 'Test Company'}
    
    with runner.isolated_filesystem():
        Path('logs').mkdir()
        result = runner.invoke(cli, ['-v', 'company-info', '28917'])
        assert result.exit_code == 0
        
        log_files = list(Path('logs').glob('sec_data_*.log'))
        assert len(log_files) > 0

def test_get_concept_success(runner, mock_sec_client):
    """Test successful concept data retrieval"""
    mock_instance = mock_sec_client.return_value
    mock_instance.get_company_concept.return_value = {
        'units': {
            'USD': [
                {'end': '2024-01-01', 'val': 1000000}
            ]
        }
    }
    
    result = runner.invoke(cli, ['get-concept', '28917', '--concept', 'Assets'])
    assert result.exit_code == 0
    assert 'USD' in result.output
    assert '1,000,000' in result.output

def test_clear_cache_success(runner):
    """Test cache clearing functionality"""
    with patch('src.utils.cache.clear_cache') as mock_clear:
        # Set up mock to return 5
        mock_clear.return_value = 5
        
        # Run command
        result = runner.invoke(cli, ['clear-sec-cache'])
        
        # Verify results
        assert result.exit_code == 0
        assert 'Cleared 5 cached responses' in result.output
        mock_clear.assert_called_once()  # Verify mock was actually called

def test_error_handling(runner, mock_sec_client):
    """Test general error handling"""
    mock_instance = mock_sec_client.return_value
    mock_instance.get_company_submissions.side_effect = Exception("Unexpected error")
    
    result = runner.invoke(cli, ['company-info', '28917'])
    assert result.exit_code == 1
    assert 'Unexpected error' in result.output

def test_analyze_peers_success(runner):
    """Test successful peer analysis"""
    with patch('src.examples.analyze_industry.analyze_company_and_peers') as mock_analyze:
        result = runner.invoke(cli, ['analyze-peers', '28917'])
        assert result.exit_code == 0
        mock_analyze.assert_called_once_with('28917')

@pytest.mark.parametrize('command,args', [
    ('company-info', []),  # Missing CIK
    ('get-concept', []),   # Missing CIK
    ('process-statements', []),  # Missing CIK
    ('analyze-peers', []),  # Missing CIK
    ('top-companies', []),  # Missing metric
])
def test_missing_required_arguments(runner, command, args):
    """Test handling of missing required arguments"""
    result = runner.invoke(cli, [command] + args)
    assert result.exit_code == 2  # Click's error code for missing arguments
    assert 'Error: Missing argument' in result.output