import logging
from typing import Dict, Any
import pandas as pd
from .base_processor import BaseProcessor, ProcessingError
from ..templates.income_statement_template import IncomeStatementTemplate

logger = logging.getLogger(__name__)

class IncomeStatementProcessor(BaseProcessor):
    """Process and standardize income statement data from SEC filings"""
    
    def __init__(self):
        super().__init__()
        self.template = IncomeStatementTemplate()
        self.required_fields = [
            'Revenue',
            'Gross Profit',
            'Operating Income',
            'Net Income (loss) (continous operations)'
        ]

    def process_company_facts(self, facts: Dict[str, Any]) -> pd.DataFrame:
        """
        Process income statement facts into standardized format
        
        Args:
            facts: Company facts from SEC API
            
        Returns:
            pd.DataFrame: Standardized income statement
            
        Raises:
            ProcessingError: If processing fails
        """
        try:
            if 'us-gaap' not in facts:
                raise ProcessingError("No US GAAP data found in company facts")

            # Extract income statement items
            is_items = {}
            for tag, data in facts['us-gaap'].items():
                if (tag in self.template.REVENUE_MAPPING or
                    tag in self.template.OPERATING_EXPENSES_MAPPING or
                    tag in self.template.OTHER_ITEMS_MAPPING):
                    
                    if 'units' in data and 'USD' in data['units']:
                        units_data = data['units']['USD']
                        # Convert list of values to DataFrame
                        tag_df = pd.DataFrame(units_data)
                        if not tag_df.empty:
                            is_items[tag] = tag_df

            if not is_items:
                raise ProcessingError("No income statement data found")

            # Combine all items into a single DataFrame
            df = pd.DataFrame()
            for tag, tag_df in is_items.items():
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
            revenue_df = self.standardize_line_items(df, self.template.REVENUE_MAPPING)
            expenses_df = self.standardize_line_items(df, self.template.OPERATING_EXPENSES_MAPPING)
            other_df = self.standardize_line_items(df, self.template.OTHER_ITEMS_MAPPING)

            # Combine all sections
            result = pd.concat([revenue_df, expenses_df, other_df], axis=1)
            
            # Add period end date
            if 'end' in df.columns:
                result['period_end_date'] = df['end']

            # Validate required fields
            self.validate_required_fields(result, self.required_fields)

            # Calculate derived fields
            result = self._calculate_derived_fields(result)

            return result

        except ProcessingError as e:
            logger.error(f"Error processing income statement: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing income statement: {str(e)}")
            raise ProcessingError(f"Failed to process income statement: {str(e)}")

    def _calculate_derived_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate derived income statement fields"""
        try:
            # Calculate gross profit margin
            if 'Gross Profit' in df.columns and 'Revenue' in df.columns:
                df['Gross Profit Margin'] = (df['Gross Profit'] / df['Revenue']) * 100

            # Calculate operating margin
            if 'Operating Income' in df.columns and 'Revenue' in df.columns:
                df['Operating Margin'] = (df['Operating Income'] / df['Revenue']) * 100

            # Calculate net profit margin
            if 'Net Income (loss) (continous operations)' in df.columns and 'Revenue' in df.columns:
                df['Net Profit Margin'] = (df['Net Income (loss) (continous operations)'] / df['Revenue']) * 100

            return df

        except Exception as e:
            logger.warning(f"Error calculating derived fields: {str(e)}")
            return df