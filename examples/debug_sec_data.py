import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import pandas as pd
from src.utils.sec_client import SECClient
from src.utils.data_processor import facts_to_dataframe
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_sec_data():
    """Load SEC data into DataFrames for inspection"""
    # Initialize client
    client = SECClient()
    
    # Get Dillard's data
    logger.info("Fetching SEC data...")
    facts = client.get_company_facts("0000028917")
    
    # Convert to DataFrames
    logger.info("Converting to DataFrames...")
    dataframes = facts_to_dataframe(facts)
    
    # Print DataFrame info
    for name, df in dataframes.items():
        logger.info(f"\nDataFrame: {name}")
        logger.info(f"Shape: {df.shape}")
        logger.info(f"Memory usage: {df.memory_usage().sum() / 1024**2:.2f} MB")
        
    return dataframes

if __name__ == "__main__":
    # Load data and keep in memory
    dfs = load_sec_data()
    
    # Keep script running for inspection
    logger.info("\nDataFrames loaded and ready for inspection.")
    logger.info("Open 'Run and Debug' sidebar (Ctrl+Shift+D) to view variables.")
    input("Press Enter to exit...")