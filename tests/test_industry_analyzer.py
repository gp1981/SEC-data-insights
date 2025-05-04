import pytest
import pandas as pd
from src.utils.industry_analyzer import IndustryAnalyzer
from unittest.mock import patch, MagicMock

@pytest.fixture
def analyzer():
    return IndustryAnalyzer()

def test_key_metrics_configuration(analyzer):
    """Test that key metrics are properly configured"""
    assert 'Assets' in analyzer.key_metrics
    assert 'Revenue' in analyzer.key_metrics
    assert 'NetIncome' in analyzer.key_metrics
    
    # Verify metric configurations
    assert analyzer.key_metrics['Assets']['tag'] == 'Assets'
    assert analyzer.key_metrics['Assets']['unit'] == 'USD'

@patch('src.utils.sec_client.SECClient.get_frames')
def test_get_industry_metrics(mock_get_frames, analyzer):
    """Test retrieving industry metrics"""
    mock_data = {
        'data': [
            {'cik': '0000001', 'val': 1000000, 'entityName': 'Company 1'},
            {'cik': '0000002', 'val': 2000000, 'entityName': 'Company 2'}
        ]
    }
    mock_get_frames.return_value = mock_data
    
    metrics = analyzer.get_industry_metrics(
        year=2024,
        quarter=4,
        metrics=['Assets']
    )
    
    assert 'Assets' in metrics
    assert isinstance(metrics['Assets'], pd.DataFrame)
    assert len(metrics['Assets']) == 2

@patch('src.utils.sec_client.SECClient.get_frames')
def test_analyze_company_position(mock_get_frames, analyzer):
    """Test company position analysis"""
    mock_data = {
        'data': [
            {'cik': '0000001', 'val': 1000000, 'entityName': 'Company 1'},
            {'cik': '0000002', 'val': 2000000, 'entityName': 'Company 2'},
            {'cik': '0000003', 'val': 3000000, 'entityName': 'Company 3'}
        ]
    }
    mock_get_frames.return_value = mock_data
    
    analysis = analyzer.analyze_company_position(
        cik='0000002',
        year=2024,
        quarter=4
    )
    
    assert not analysis.empty
    assert 'percentile' in analysis.columns
    assert 'company_value' in analysis.columns
    assert 'industry_median' in analysis.columns
    
    # Company 2 should be at the 50th percentile
    company_row = analysis[analysis['company_value'] == 2000000].iloc[0]
    assert 33.0 < company_row['percentile'] < 67.0

@patch('src.utils.sec_client.SECClient.get_frames')
def test_get_peer_rankings(mock_get_frames, analyzer):
    """Test peer ranking functionality"""
    mock_data = {
        'data': [
            {'cik': '0000001', 'val': 1000000, 'entityName': 'Company 1'},
            {'cik': '0000002', 'val': 2000000, 'entityName': 'Company 2'},
            {'cik': '0000003', 'val': 3000000, 'entityName': 'Company 3'},
            {'cik': '0000004', 'val': 4000000, 'entityName': 'Company 4'},
            {'cik': '0000005', 'val': 5000000, 'entityName': 'Company 5'}
        ]
    }
    mock_get_frames.return_value = mock_data
    
    rankings = analyzer.get_peer_rankings(
        metric='Revenue',
        year=2024,
        quarter=4,
        top_n=3
    )
    
    assert len(rankings) == 3
    assert list(rankings['entityName']) == ['Company 5', 'Company 4', 'Company 3']

def test_invalid_metric(analyzer):
    """Test handling of invalid metrics"""
    with pytest.raises(ValueError):
        analyzer.get_peer_rankings(
            metric='InvalidMetric',
            year=2024,
            quarter=4
        )

@patch('src.utils.sec_client.SECClient.get_frames')
def test_empty_response_handling(mock_get_frames, analyzer):
    """Test handling of empty API responses"""
    mock_get_frames.return_value = {'data': []}
    
    metrics = analyzer.get_industry_metrics(
        year=2024,
        quarter=4,
        metrics=['Assets']
    )
    
    assert 'Assets' in metrics
    assert metrics['Assets'].empty