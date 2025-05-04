import json
from datetime import datetime
from typing import Dict, Any
from src.models.company_data import Company, CompanyTicker, CompanyExchange, Filing, Session

class SECDataProcessor:
    def __init__(self, json_file_path: str):
        """Initialize the processor with path to JSON file"""
        self.json_file_path = json_file_path
        self.session = Session()

    def load_json_data(self) -> Dict[str, Any]:
        """Load JSON data from file"""
        with open(self.json_file_path, 'r') as file:
            return json.load(file)

    def parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None

    def parse_datetime(self, datetime_str: str) -> datetime:
        """Parse datetime string to datetime object"""
        if not datetime_str:
            return None
        try:
            return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        except (ValueError, TypeError):
            return None

    def process_data(self):
        """Process JSON data and store in database"""
        data = self.load_json_data()
        
        try:
            # Check if company already exists
            existing_company = self.session.query(Company).filter(Company.cik == data['cik']).first()
            
            if existing_company:
                # Update existing company
                existing_company.entity_type = data.get('entity_type')
                existing_company.sic = data.get('sic')
                existing_company.sic_description = data.get('sic_description')
                existing_company.name = data.get('name')
                existing_company.fiscal_year_end = data.get('fiscal_year_end')
                company = existing_company
            else:
                # Create new company record
                company = Company(
                    cik=data['cik'],
                    entity_type=data.get('entity_type'),
                    sic=data.get('sic'),
                    sic_description=data.get('sic_description'),
                    name=data.get('name'),
                    fiscal_year_end=data.get('fiscal_year_end')
                )
                self.session.add(company)
            
            self.session.flush()  # Get company ID

            # Clear existing tickers and exchanges
            if existing_company:
                self.session.query(CompanyTicker).filter(CompanyTicker.company_id == company.id).delete()
                self.session.query(CompanyExchange).filter(CompanyExchange.company_id == company.id).delete()

            # Add tickers
            for ticker in data.get('tickers', []):
                company_ticker = CompanyTicker(
                    company_id=company.id,
                    ticker=ticker
                )
                self.session.add(company_ticker)

            # Add exchanges
            for exchange in data.get('exchanges', []):
                company_exchange = CompanyExchange(
                    company_id=company.id,
                    exchange=exchange
                )
                self.session.add(company_exchange)

            # Process filings
            if 'filings' in data and 'recent' in data['filings']:
                recent_filings = zip(
                    data['filings']['recent'].get('accessionNumber', []),
                    data['filings']['recent'].get('filingDate', []),
                    data['filings']['recent'].get('reportDate', []),
                    data['filings']['recent'].get('acceptanceDateTime', []),
                    data['filings']['recent'].get('act', []),
                    data['filings']['recent'].get('form', []),
                    data['filings']['recent'].get('fileNumber', []),
                    data['filings']['recent'].get('filmNumber', []),
                    data['filings']['recent'].get('items', []),
                    data['filings']['recent'].get('core_type', []),
                    data['filings']['recent'].get('size', []),
                    data['filings']['recent'].get('isXBRL', []),
                    data['filings']['recent'].get('isInlineXBRL', []),
                    data['filings']['recent'].get('primaryDocument', []),
                    data['filings']['recent'].get('primaryDocDescription', [])
                )

                for filing_data in recent_filings:
                    (accession_number, filing_date, report_date, acceptance_datetime,
                     act, form, file_number, film_number, items, core_type, size,
                     is_xbrl, is_inline_xbrl, primary_document, primary_doc_description) = filing_data

                    # Check if filing already exists
                    existing_filing = self.session.query(Filing).filter(
                        Filing.accession_number == accession_number
                    ).first()

                    if not existing_filing:
                        filing = Filing(
                            company_id=company.id,
                            accession_number=accession_number,
                            filing_date=self.parse_date(filing_date),
                            report_date=self.parse_date(report_date),
                            acceptance_datetime=self.parse_datetime(acceptance_datetime),
                            act=act,
                            form=form,
                            file_number=file_number,
                            film_number=film_number,
                            items=items,
                            core_type=core_type,
                            size=size,
                            is_xbrl=bool(is_xbrl),
                            is_inline_xbrl=bool(is_inline_xbrl),
                            primary_document=primary_document,
                            primary_doc_description=primary_doc_description
                        )
                        self.session.add(filing)

            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            raise e

        finally:
            self.session.close()

    def query_filings(self, form_type: str = None, start_date: str = None, end_date: str = None):
        """Query filings with optional filters"""
        query = self.session.query(Filing).join(Company)
        
        if form_type:
            query = query.filter(Filing.form == form_type)
        
        if start_date:
            start_date = self.parse_date(start_date)
            query = query.filter(Filing.filing_date >= start_date)
            
        if end_date:
            end_date = self.parse_date(end_date)
            query = query.filter(Filing.filing_date <= end_date)
            
        return query.all()

    def get_company_info(self, cik: str = None):
        """Get company information"""
        query = self.session.query(Company)
        if cik:
            query = query.filter(Company.cik == cik)
        return query.first()