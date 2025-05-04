from typing import Dict, Any
import pandas as pd
import logging
from .base_processor import BaseProcessor, ProcessingError
from ..templates.cash_flow_template import CashFlowTemplate

logger = logging.getLogger(__name__)

class CashFlowProcessor(BaseProcessor):
    """Process and standardize cash flow statement data from SEC filings"""
    
    def __init__(self):
        super().__init__()
        self.template = CashFlowTemplate()
        self.required_fields = [
            '(Operating Activities) Cash Flow from Operating Activities',
            '(Investing Activities) Cash Flow from Investing Activities',
            '(Financing Activities) Cash Flow from Financing Activities'
        ]

    def process_company_facts(self, facts: Dict[str, Any]) -> pd.DataFrame:
        """
        Process cash flow facts into standardized format
        
        Args:
            facts: Company facts from SEC API
            
        Returns:
            pd.DataFrame: Standardized cash flow statement
            
        Raises:
            ProcessingError: If processing fails
        """
        try:
            if 'us-gaap' not in facts:
                raise ProcessingError("No US GAAP data found in company facts")

            # Extract cash flow items
            cf_items = {}
            for tag, data in facts['us-gaap'].items():
                if (tag in self.template.OPERATING_ACTIVITIES_MAPPING or
                    tag in self.template.INVESTING_ACTIVITIES_MAPPING or
                    tag in self.template.FINANCING_ACTIVITIES_MAPPING):
                    
                    if 'units' in data and 'USD' in data['units']:
                        units_data = data['units']['USD']
                        # Convert list of values to DataFrame
                        tag_df = pd.DataFrame(units_data)
                        if not tag_df.empty:
                            cf_items[tag] = tag_df

            if not cf_items:
                raise ProcessingError("No cash flow data found")

            # Combine all items into a single DataFrame
            df = pd.DataFrame()
            for tag, tag_df in cf_items.items():
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
            operating_df = self.standardize_line_items(df, self.template.OPERATING_ACTIVITIES_MAPPING)
            investing_df = self.standardize_line_items(df, self.template.INVESTING_ACTIVITIES_MAPPING)
            financing_df = self.standardize_line_items(df, self.template.FINANCING_ACTIVITIES_MAPPING)

            # Combine all sections
            result = pd.concat([operating_df, investing_df, financing_df], axis=1)
            
            # Add period end date
            if 'end' in df.columns:
                result['period_end_date'] = df['end']

            # Validate required fields
            self.validate_required_fields(result, self.required_fields)

            # Calculate derived fields
            result = self._calculate_derived_fields(result)

            return result

        except ProcessingError as e:
            logger.error(f"Error processing cash flow statement: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing cash flow statement: {str(e)}")
            raise ProcessingError(f"Failed to process cash flow statement: {str(e)}")

    def _calculate_derived_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate derived cash flow fields"""
        try:
            # Calculate free cash flow
            if ('(Operating Activities) Cash Flow from Operating Activities' in df.columns and 
                '(Investing Activities) Purchase of Property, Plant and Equipment' in df.columns):
                df['Free Cash Flow'] = (
                    df['(Operating Activities) Cash Flow from Operating Activities'] - 
                    abs(df['(Investing Activities) Purchase of Property, Plant and Equipment'])
                )

            # Calculate total cash flow
            required_fields = [
                '(Operating Activities) Cash Flow from Operating Activities',
                '(Investing Activities) Cash Flow from Investing Activities',
                '(Financing Activities) Cash Flow from Financing Activities'
            ]
            
            if all(field in df.columns for field in required_fields):
                df['Total Cash Flow'] = (
                    df['(Operating Activities) Cash Flow from Operating Activities'] +
                    df['(Investing Activities) Cash Flow from Investing Activities'] +
                    df['(Financing Activities) Cash Flow from Financing Activities']
                )

            # Calculate operating cash flow ratio
            if ('(Operating Activities) Cash Flow from Operating Activities' in df.columns and 
                'Total Current Liabilities' in df.columns and
                df['Total Current Liabilities'].any()):  # Check for non-zero values
                df['Operating Cash Flow Ratio'] = (
                    df['(Operating Activities) Cash Flow from Operating Activities'] / 
                    df['Total Current Liabilities']
                )

            return df

        except Exception as e:
            logger.warning(f"Error calculating derived fields: {str(e)}")
            return df