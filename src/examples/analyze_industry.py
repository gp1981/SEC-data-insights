import logging
from typing import Dict, Any, Optional
from datetime import datetime

from src.utils.sec_client import SECClient
from src.utils.industry_analyzer import IndustryAnalyzer

logger = logging.getLogger(__name__)

def analyze_company_and_peers(cik: str) -> None:
    """Analyze a company's position relative to its industry peers
    
    Args:
        cik: Company CIK number
    """
    try:
        # Get company info
        client = SECClient()
        company_info = client.get_company_submissions(cik)
        company_name = company_info.get('name', cik)
        
        # Initialize analyzer
        analyzer = IndustryAnalyzer()
        
        # Get latest year's metrics
        current_year = datetime.now().year
        metrics = analyzer.get_industry_metrics(
            company_info.get('sic'),
            year=current_year-1  # Use previous year for complete data
        )
        
        if not metrics.empty:
            print(f"\nIndustry Analysis for {company_name}")
            print("=" * 50)
            
            # Get company's position for each metric
            position = analyzer.analyze_company_position(cik, metrics)
            for metric, percentile in position.items():
                print(f"{metric}: {percentile:.1f}th percentile")
                
            # Show top companies for a few key metrics
            key_metrics = ['Assets', 'Revenues', 'NetIncomeLoss']
            for metric in key_metrics:
                print(f"\nTop 5 Companies by {metric}:")
                rankings = analyzer.get_peer_rankings(
                    metric=metric,
                    year=current_year-1,
                    top_n=5
                )
                for _, row in rankings.iterrows():
                    print(f"{row['entityName']}: {row['val']:,.0f}")
        else:
            print("No industry data available for analysis")
            
    except Exception as e:
        logger.error(f"Error analyzing company {cik}: {str(e)}")
        raise

def main():
    # Example usage
    cik = "0000320193"  # Apple Inc.
    analyze_company_and_peers(cik)

if __name__ == "__main__":
    main()