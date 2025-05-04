import logging
from typing import Dict, Any
import pandas as pd
from .base_processor import BaseProcessor, ProcessingError
from ..templates.balance_sheet_template import BalanceSheetTemplate

logger = logging.getLogger(__name__)

class BalanceSheetProcessor(BaseProcessor):
    """Process and standardize balance sheet data from SEC filings"""
    
    def __init__(self):
        super().__init__()
        self.template = BalanceSheetTemplate()
        self.required_fields = [
            'Total Assets',
            'Total Liabilities',
            'Total Stockholders Equity'
        ]

    def process_company_facts(self, facts: Dict[str, Any]) -> pd.DataFrame:
        """
        Process balance sheet facts into standardized format
        
        Args:
            facts: Company facts from SEC API
            
        Returns:
            pd.DataFrame: Standardized balance sheet
            
        Raises:
            ProcessingError: If processing fails
        """
        try:
            if 'us-gaap' not in facts:
                raise ProcessingError("No US GAAP data found in company facts")

            # Extract balance sheet items
            bs_items = {}
            for tag, data in facts['us-gaap'].items():
                if (tag in self.template.ASSETS_MAPPING or
                    tag in self.template.LIABILITIES_MAPPING or
                    tag in self.template.EQUITY_MAPPING):
                    
                    if 'units' in data and 'USD' in data['units']:
                        units_data = data['units']['USD']
                        # Convert list of values to DataFrame
                        tag_df = pd.DataFrame(units_data)
                        if not tag_df.empty:
                            bs_items[tag] = tag_df

            if not bs_items:
                raise ProcessingError("No balance sheet data found")

            # Combine all items into a single DataFrame
            df = pd.DataFrame()
            for tag, tag_df in bs_items.items():
                if 'val' in tag_df.columns and 'end' in tag_df.columns:
                    tag_df = tag_df[['end', 'val']].copy()
                    tag_df.columns = ['end', tag]
                    if df.empty:
                        df = tag_df
                    else:
                        df = pd.merge(df, tag_df, on='end', how='outer')

            # Process dates
            df = self.process_dates(df)

            # Standardize using template mappings
            assets_df = self.standardize_line_items(df, self.template.ASSETS_MAPPING)
            liab_df = self.standardize_line_items(df, self.template.LIABILITIES_MAPPING)
            equity_df = self.standardize_line_items(df, self.template.EQUITY_MAPPING)

            # Combine all sections
            result = pd.concat([assets_df, liab_df, equity_df], axis=1)
            
            # Add period end date
            if 'end' in df.columns:
                result['period_end_date'] = df['end']

            # Validate required fields
            self.validate_required_fields(result, self.required_fields)

            # Calculate derived fields
            result = self._calculate_derived_fields(result)

            return result

        except ProcessingError as e:
            logger.error(f"Error processing balance sheet: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing balance sheet: {str(e)}")
            raise ProcessingError(f"Failed to process balance sheet: {str(e)}")

    def _calculate_derived_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate derived balance sheet fields"""
        try:
            # Calculate working capital
            if 'Total Current Assets' in df.columns and 'Total Current Liabilities' in df.columns:
                df['Working Capital'] = df['Total Current Assets'] - df['Total Current Liabilities']

            # Calculate total assets verification
            if 'Total Current Assets' in df.columns and 'Total Non Current Assets' in df.columns:
                df['Total Assets (Calculated)'] = df['Total Current Assets'] + df['Total Non Current Assets']

            # Calculate debt to equity ratio
            if 'Total Liabilities' in df.columns and 'Total Stockholders Equity' in df.columns:
                df['Debt to Equity Ratio'] = df['Total Liabilities'] / df['Total Stockholders Equity']

            return df

        except Exception as e:
            logger.warning(f"Error calculating derived fields: {str(e)}")
            return df