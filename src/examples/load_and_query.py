from src.data.sec_data_processor import SECDataProcessor
import pandas as pd

def main():
    # Initialize the data processor
    processor = SECDataProcessor('company_data.json')
    
    # Load data into database
    print("Loading data into database...")
    processor.process_data()
    
    # Example 1: Get all 10-K filings
    print("\nQuerying 10-K filings:")
    filings_10k = processor.query_filings(form_type='10-K')
    df_10k = pd.DataFrame([{
        'filing_date': f.filing_date,
        'report_date': f.report_date,
        'accession_number': f.accession_number,
        'form': f.form,
        'company_name': f.company.name
    } for f in filings_10k])
    print(df_10k)
    
    # Example 2: Get company information
    print("\nQuerying company information:")
    company = processor.get_company_info()
    if company:
        print(f"Company: {company.name}")
        print(f"CIK: {company.cik}")
        print(f"SIC: {company.sic} - {company.sic_description}")
        print("\nTickers:")
        for ticker in company.tickers:
            print(f"- {ticker.ticker}")
        print("\nExchanges:")
        for exchange in company.exchanges:
            print(f"- {exchange.exchange}")
    
    # Example 3: Get recent filings from 2024
    print("\nQuerying 2024 filings:")
    filings_2024 = processor.query_filings(start_date='2024-01-01', end_date='2024-12-31')
    df_2024 = pd.DataFrame([{
        'filing_date': f.filing_date,
        'form': f.form,
        'accession_number': f.accession_number
    } for f in filings_2024])
    print(df_2024)

if __name__ == '__main__':
    main()