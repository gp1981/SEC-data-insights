from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import logging
from sqlalchemy import Column, Integer, String, Date, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..config.database import Base, Session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CompanyData:
    """
    Data class representing SEC company submission data
    """
    cik: str
    entity_type: str
    sic: str
    sic_description: str
    name: str
    tickers: List[str]
    exchanges: List[str]
    fiscal_year_end: str
    filings: Dict[str, Any]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'CompanyData':
        """
        Create a CompanyData instance from SEC API JSON response
        
        Args:
            data (Dict[str, Any]): JSON response from SEC API
            
        Returns:
            CompanyData: Structured company data
            
        Raises:
            ValueError: If required fields are missing from the data
        """
        try:
            return cls(
                cik=str(data.get('cik')),
                entity_type=data.get('entityType', ''),
                sic=str(data.get('sic')),
                sic_description=data.get('sicDescription', ''),
                name=data.get('name', ''),
                tickers=data.get('tickers', []),
                exchanges=data.get('exchanges', []),
                fiscal_year_end=data.get('fiscalYearEnd', ''),
                filings=data.get('filings', {})
            )
        except Exception as e:
            logger.error(f"Error creating CompanyData from JSON: {str(e)}")
            raise ValueError(f"Failed to create CompanyData: {str(e)}")

    def get_recent_filings(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Get the n most recent filings
        
        Args:
            n (int): Number of recent filings to return
            
        Returns:
            List[Dict[str, Any]]: List of recent filings
        """
        try:
            if 'recent' not in self.filings:
                logger.warning(f"No recent filings found for CIK {self.cik}")
                return []
            
            return self.filings['recent'].get('files', [])[:n]
        except Exception as e:
            logger.error(f"Error retrieving recent filings: {str(e)}")
            return []

    def get_filing_details(self, form_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get filing details, optionally filtered by form type
        
        Args:
            form_type (str, optional): Type of form to filter by (e.g., '10-K', '10-Q')
            
        Returns:
            List[Dict[str, Any]]: List of filings matching the criteria
        """
        try:
            if 'recent' not in self.filings:
                logger.warning(f"No recent filings found for CIK {self.cik}")
                return []

            filings = self.filings['recent'].get('files', [])
            if form_type:
                return [f for f in filings if f.get('form') == form_type]
            return filings
        except Exception as e:
            logger.error(f"Error retrieving filing details: {str(e)}")
            return []
    
    def process_financial_statements(self) -> Dict[str, pd.DataFrame]:
        """
        Process all financial statements for the company
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing processed financial statements
        """
        from ..processors.balance_sheet_processor import BalanceSheetProcessor
        from ..processors.income_statement_processor import IncomeStatementProcessor
        from ..processors.cash_flow_processor import CashFlowProcessor
        
        processors = {
            'balance_sheet': BalanceSheetProcessor(),
            'income_statement': IncomeStatementProcessor(),
            'cash_flow': CashFlowProcessor()
        }
        
        results = {}
        for statement_type, processor in processors.items():
            try:
                logger.info(f"Processing {statement_type} for CIK {self.cik}")
                results[statement_type] = processor.process_company_facts(self.filings)
            except Exception as e:
                logger.error(f"Error processing {statement_type}: {str(e)}")
                results[statement_type] = pd.DataFrame()
        
        return results

# Database Models
class Company(Base):
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True)
    cik = Column(String, unique=True, nullable=False, index=True)
    entity_type = Column(String)
    sic = Column(String, index=True)
    sic_description = Column(String)
    name = Column(String, index=True)
    fiscal_year_end = Column(String)
    
    # Relationships
    filings = relationship("Filing", back_populates="company", cascade="all, delete-orphan")
    tickers = relationship("CompanyTicker", back_populates="company", cascade="all, delete-orphan")
    exchanges = relationship("CompanyExchange", back_populates="company", cascade="all, delete-orphan")

class CompanyTicker(Base):
    __tablename__ = 'company_tickers'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    ticker = Column(String, nullable=False, index=True)
    
    # Relationships
    company = relationship("Company", back_populates="tickers")

class CompanyExchange(Base):
    __tablename__ = 'company_exchanges'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    exchange = Column(String, nullable=False, index=True)
    
    # Relationships
    company = relationship("Company", back_populates="exchanges")

class Filing(Base):
    __tablename__ = 'filings'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    accession_number = Column(String, unique=True, nullable=False, index=True)
    filing_date = Column(Date, index=True)
    report_date = Column(Date, index=True)
    acceptance_datetime = Column(Date)
    act = Column(String)
    form = Column(String, index=True)
    file_number = Column(String)
    film_number = Column(String)
    items = Column(String)
    core_type = Column(String)
    size = Column(Integer)
    is_xbrl = Column(Boolean)
    is_inline_xbrl = Column(Boolean)
    primary_document = Column(String)
    primary_doc_description = Column(String)
    
    # Relationships
    company = relationship("Company", back_populates="filings")
