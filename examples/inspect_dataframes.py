import pandas as pd
from src.utils.sec_client import SECClient
from src.utils.data_processor import facts_to_dataframe

def inspect_company_data(cik: str):
    """Load and inspect company facts data"""
    client = SECClient()
    facts = client.get_company_facts(cik)
    dfs = facts_to_dataframe(facts)
    
    # This will trigger VSCode's Data Wrangler
    return dfs

# Run for Dillard's
if __name__ == "__main__":
    dataframes = inspect_company_data("0000028917")
    # Keep variables in memory for Data Wrangler
    globals().update(dataframes)