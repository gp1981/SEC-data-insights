from src.utils.sec_client import SECClient
from src.utils.data_processor import facts_to_dataframe
import pandas as pd
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Initialize SEC client
    client = SECClient()
    
    # Download facts for Dillard's (CIK: 0000028917)
    logger.info("Downloading SEC facts...")
    facts = client.get_company_facts("0000028917")
    
    # Convert facts to DataFrames
    logger.info("Converting to DataFrames...")
    dataframes = facts_to_dataframe(facts)
    
    # Example: Work with specific metrics
    revenue_df = next((df for name, df in dataframes.items() if 'Revenue' in name), None)
    
    if revenue_df is not None:
        logger.info("\nRevenue Data:")
        logger.info(f"Shape: {revenue_df.shape}")
        logger.info("\nFirst 5 records:")
        print(revenue_df.info())
        print(revenue_df.head())
    
    return dataframes

if __name__ == "__main__":
    dfs = main()
    
    # Keep script running for debugging
    logger.info("\nDataFrames stored in 'dfs' variable")
    input("Press Enter to exit...")