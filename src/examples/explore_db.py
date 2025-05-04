import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.db_explorer import DBExplorer

def main():
    explorer = DBExplorer()
    
    # List all tables
    explorer.list_tables()
    
    # Show schema for each table
    tables = ['companies', 'company_tickers', 'company_exchanges', 'filings']
    for table in tables:
        explorer.table_info(table)
    
    # Preview data in each table
    for table in tables:
        explorer.preview_table(table)
    
    # Example of custom queries
    print("\nCustom Query Examples:")
    
    # 1. Count filings by form type
    explorer.custom_query("""
        SELECT form, COUNT(*) as count
        FROM filings
        GROUP BY form
        ORDER BY count DESC;
    """)
    
    # 2. Get company details with ticker and exchange
    explorer.custom_query("""
        SELECT c.name, c.cik, ct.ticker, ce.exchange
        FROM companies c
        LEFT JOIN company_tickers ct ON c.id = ct.company_id
        LEFT JOIN company_exchanges ce ON c.id = ce.company_id;
    """)
    
    # 3. Get recent filings with company info
    explorer.custom_query("""
        SELECT c.name, f.form, f.filing_date, f.accession_number
        FROM filings f
        JOIN companies c ON f.company_id = c.id
        ORDER BY f.filing_date DESC
        LIMIT 10;
    """)
    
    explorer.close()

if __name__ == '__main__':
    main()