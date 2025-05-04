from typing import Dict, Any, List, Optional
import pandas as pd
import logging
from datetime import datetime
from .sec_client import SECClient

logger = logging.getLogger(__name__)

class IndustryAnalyzer:
    """Utility class for analyzing company performance against industry peers"""

    def __init__(self, sec_client: Optional[SECClient] = None):
        self.client = sec_client or SECClient()
        self.key_metrics = {
            'Assets': {'tag': 'Assets', 'unit': 'USD'},
            'Revenue': {'tag': 'Revenues', 'unit': 'USD'},
            'NetIncome': {'tag': 'NetIncomeLoss', 'unit': 'USD'},
            'OperatingIncome': {'tag': 'OperatingIncomeLoss', 'unit': 'USD'},
            'EarningsPerShare': {'tag': 'EarningsPerShareDiluted', 'unit': 'USD-per-shares'}
        }

    def get_industry_metrics(self, 
                           year: int,
                           quarter: Optional[int] = None,
                           metrics: Optional[List[str]] = None) -> Dict[str, pd.DataFrame]:
        """
        Retrieve industry-wide metrics for comparison
        
        Args:
            year: Year to analyze
            quarter: Optional quarter (1-4)
            metrics: List of metrics to retrieve (defaults to all key metrics)
            
        Returns:
            Dict[str, pd.DataFrame]: Industry metrics by category
        """
        metrics = metrics or list(self.key_metrics.keys())
        results = {}
        
        for metric in metrics:
            if metric not in self.key_metrics:
                logger.warning(f"Unsupported metric: {metric}")
                continue
                
            try:
                config = self.key_metrics[metric]
                frame_data = self.client.get_frames(
                    taxonomy="us-gaap",
                    tag=config['tag'],
                    unit=config['unit'],
                    year=year,
                    quarter=quarter
                )
                
                if 'data' in frame_data:
                    df = pd.DataFrame(frame_data['data'])
                    results[metric] = df
                    
            except Exception as e:
                logger.error(f"Error retrieving {metric}: {str(e)}")
                
        return results

    def analyze_company_position(self,
                               cik: str,
                               year: int,
                               quarter: Optional[int] = None,
                               metrics: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Analyze a company's position relative to industry peers
        
        Args:
            cik: Company CIK number
            year: Year to analyze
            quarter: Optional quarter (1-4)
            metrics: List of metrics to analyze
            
        Returns:
            pd.DataFrame: Analysis results including percentile rankings
        """
        industry_data = self.get_industry_metrics(year, quarter, metrics)
        results = []
        
        for metric, df in industry_data.items():
            if df is None or df.empty:
                continue
                
            try:
                # Find company's value
                company_row = df[df['cik'] == cik]
                if company_row.empty:
                    continue
                    
                company_value = company_row['val'].iloc[0]
                
                # Calculate statistics
                stats = df['val'].describe()
                percentile = (df['val'] <= company_value).mean() * 100
                
                results.append({
                    'metric': metric,
                    'company_value': company_value,
                    'industry_median': stats['50%'],
                    'industry_mean': stats['mean'],
                    'percentile': percentile,
                    'num_companies': len(df),
                    'period': f"{'Q'+str(quarter) if quarter else 'FY'}{year}"
                })
                
            except Exception as e:
                logger.error(f"Error analyzing {metric}: {str(e)}")
                
        return pd.DataFrame(results)

    def get_peer_rankings(self,
                         metric: str,
                         year: int,
                         quarter: Optional[int] = None,
                         top_n: int = 10) -> pd.DataFrame:
        """
        Get top companies by a specific metric
        
        Args:
            metric: Metric to rank by
            year: Year to analyze
            quarter: Optional quarter (1-4)
            top_n: Number of companies to return
            
        Returns:
            pd.DataFrame: Top companies ranked by the metric
        """
        if metric not in self.key_metrics:
            raise ValueError(f"Unsupported metric: {metric}")
            
        try:
            config = self.key_metrics[metric]
            frame_data = self.client.get_frames(
                taxonomy="us-gaap",
                tag=config['tag'],
                unit=config['unit'],
                year=year,
                quarter=quarter
            )
            
            if 'data' in frame_data:
                df = pd.DataFrame(frame_data['data'])
                if not df.empty:
                    # Sort by value and get top N
                    top_companies = df.nlargest(top_n, 'val')
                    
                    # Format values
                    if config['unit'] == 'USD':
                        top_companies['val'] = top_companies['val'].map('${:,.0f}'.format)
                    else:
                        top_companies['val'] = top_companies['val'].map('{:,.2f}'.format)
                        
                    return top_companies[['entityName', 'val', 'cik']]
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error getting peer rankings: {str(e)}")
            return pd.DataFrame()