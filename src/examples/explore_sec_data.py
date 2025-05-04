import sys
from pathlib import Path
import logging
import pandas as pd
from datetime import datetime

# Add the src directory to the Python path
src_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(src_dir))

from utils.sec_client import SECClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def explore_company_data(cik: str):
    """
    Demonstrates retrieving and analyzing various types of SEC data for a company
    
    Args:
        cik: Company CIK number
    """
    client = SECClient()
    
    try:
        # 1. Get company submissions data
        logger.info(f"Retrieving submission data for CIK {cik}")
        submissions = client.get_company_submissions(cik)
        print("\nCompany Information:")
        print(f"Name: {submissions.get('name')}")
        print(f"Tickers: {', '.join(submissions.get('tickers', []))}")
        print(f"SIC: {submissions.get('sicDescription')}")
        
        # 2. Get recent filings
        recent_filings = submissions.get('filings', {}).get('recent', {}).get('files', [])
        print("\nMost Recent Filings:")
        for filing in recent_filings[:5]:
            print(f"Form {filing.get('form')} filed on {filing.get('filingDate')}")
        
        # 3. Get specific concept data (e.g., Assets)
        logger.info("Retrieving Assets concept data")
        assets_concept = client.get_company_concept(cik, "us-gaap", "Assets")
        if 'units' in assets_concept and 'USD' in assets_concept['units']:
            assets_df = pd.DataFrame(assets_concept['units']['USD'])
            print("\nAssets Over Time:")
            print(assets_df[['end', 'val']].tail())
        
        # 4. Get company facts
        logger.info("Retrieving company facts")
        facts = client.get_company_facts(cik)
        us_gaap_facts = facts.get('facts', {}).get('us-gaap', {})
        print(f"\nNumber of GAAP concepts available: {len(us_gaap_facts)}")
        
        # 5. Get frame data for comparison
        logger.info("Retrieving frame data for comparison")
        current_year = datetime.now().year
        assets_frame = client.get_frames(
            taxonomy="us-gaap",
            tag="Assets",
            unit="USD",
            year=current_year - 1,  # Previous year
            quarter=4
        )
        
        if 'data' in assets_frame:
            frame_df = pd.DataFrame(assets_frame['data'])
            print("\nIndustry Comparison (Assets):")
            print(frame_df.describe())
        
    except Exception as e:
        logger.error(f"Error exploring company data: {str(e)}")
        raise

def explore_financial_metrics(cik: str):
    """
    Demonstrates analyzing specific financial metrics using various SEC endpoints
    
    Args:
        cik: Company CIK number
    """
    client = SECClient()
    
    try:
        # Get key financial metrics using company concepts
        metrics = {
            'Revenue': 'Revenues',
            'Net Income': 'NetIncomeLoss',
            'Operating Income': 'OperatingIncomeLoss',
            'Total Assets': 'Assets',
            'Total Liabilities': 'Liabilities'
        }
        
        results = {}
        for label, tag in metrics.items():
            try:
                data = client.get_company_concept(cik, "us-gaap", tag)
                if 'units' in data and 'USD' in data['units']:
                    df = pd.DataFrame(data['units']['USD'])
                    df = df.sort_values('end', ascending=False)
                    results[label] = df.iloc[0]['val'] if not df.empty else None
            except Exception as e:
                logger.warning(f"Could not retrieve {label}: {str(e)}")
                results[label] = None
        
        print("\nKey Financial Metrics (Most Recent):")
        for label, value in results.items():
            if value is not None:
                print(f"{label}: ${value:,.2f}")
            else:
                print(f"{label}: Not available")
                
    except Exception as e:
        logger.error(f"Error analyzing financial metrics: {str(e)}")
        raise

def main():
    # Example usage with Dillard's Inc.
    CIK = "28917"  # Dillard's Inc.
    
    print("=== SEC Data Explorer ===")
    explore_company_data(CIK)
    print("\n=== Financial Metrics Analysis ===")
    explore_financial_metrics(CIK)

if __name__ == "__main__":
    main()