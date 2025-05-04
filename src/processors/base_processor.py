from typing import Dict, Any, Optional, List
import pandas as pd
from abc import ABC, abstractmethod
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ProcessingError(Exception):
    """Exception raised for errors during financial statement processing"""
    pass

class BaseProcessor(ABC):
    """Abstract base class for financial statement processors with enhanced SEC data support"""

    def __init__(self):
        self.template = None

    @abstractmethod
    def process_company_facts(self, facts: Dict[str, Any]) -> pd.DataFrame:
        """
        Process company facts into standardized financial statements
        
        Args:
            facts: Raw company facts from SEC API
            
        Returns:
            pd.DataFrame: Standardized financial statement
            
        Raises:
            ProcessingError: If processing fails
        """
        pass

    def process_concept_data(self, concept_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Process data from SEC company concept endpoint
        
        Args:
            concept_data: Raw concept data from SEC API
            
        Returns:
            pd.DataFrame: Processed concept data
            
        Raises:
            ProcessingError: If processing fails
        """
        try:
            if 'units' not in concept_data:
                raise ProcessingError("No units data found in concept data")

            dfs = []
            for unit, values in concept_data['units'].items():
                df = pd.DataFrame(values)
                df['unit'] = unit
                dfs.append(df)

            if not dfs:
                raise ProcessingError("No data found in concept")

            result = pd.concat(dfs, ignore_index=True)
            result = self.process_dates(result)
            return result

        except Exception as e:
            logger.error(f"Error processing concept data: {str(e)}")
            raise ProcessingError(f"Failed to process concept data: {str(e)}")

    def process_frame_data(self, frame_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Process data from SEC frames endpoint
        
        Args:
            frame_data: Raw frame data from SEC API
            
        Returns:
            pd.DataFrame: Processed frame data
            
        Raises:
            ProcessingError: If processing fails
        """
        try:
            if 'data' not in frame_data:
                raise ProcessingError("No data found in frame")

            df = pd.DataFrame(frame_data['data'])
            df = self.process_dates(df)
            return df

        except Exception as e:
            logger.error(f"Error processing frame data: {str(e)}")
            raise ProcessingError(f"Failed to process frame data: {str(e)}")

    def standardize_line_items(self, df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
        """
        Standardize line items using template mapping
        
        Args:
            df: DataFrame containing raw financial data
            mapping: Dictionary mapping SEC tags to standardized names
            
        Returns:
            pd.DataFrame: Standardized financial data
            
        Raises:
            ProcessingError: If standardization fails
        """
        try:
            standardized_df = pd.DataFrame()
            
            for sec_tag, standard_name in mapping.items():
                if sec_tag in df.columns:
                    standardized_df[standard_name] = df[sec_tag]
                else:
                    logger.debug(f"SEC tag {sec_tag} not found in data")
            
            return standardized_df
            
        except Exception as e:
            logger.error(f"Error standardizing line items: {str(e)}")
            raise ProcessingError(f"Failed to standardize line items: {str(e)}")
            
    def validate_required_fields(self, df: pd.DataFrame, required_fields: list) -> bool:
        """
        Validate that required fields are present in the DataFrame
        
        Args:
            df: DataFrame to validate
            required_fields: List of required field names
            
        Returns:
            bool: True if all required fields are present
            
        Raises:
            ProcessingError: If required fields are missing
        """
        missing_fields = [field for field in required_fields if field not in df.columns]
        if missing_fields:
            raise ProcessingError(f"Missing required fields: {', '.join(missing_fields)}")
        return True
        
    def process_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert date columns to datetime format
        
        Args:
            df: DataFrame containing date columns
            
        Returns:
            pd.DataFrame: DataFrame with processed dates
        """
        try:
            date_columns = [col for col in df.columns 
                          if any(date_term in col.lower() 
                                for date_term in ['date', 'period', 'end', 'start'])]
            
            for col in date_columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                
            return df
            
        except Exception as e:
            logger.warning(f"Error processing dates: {str(e)}")
            return df

    def calculate_period_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate period-over-period metrics
        
        Args:
            df: DataFrame with time series data
            
        Returns:
            pd.DataFrame: DataFrame with additional metrics
        """
        try:
            if 'val' in df.columns and 'end' in df.columns:
                # Sort by date
                df = df.sort_values('end')
                
                # Calculate period-over-period changes
                df['change_from_previous'] = df['val'].diff()
                df['pct_change_from_previous'] = df['val'].pct_change() * 100
                
                # Calculate year-over-year changes
                df['change_from_previous_year'] = df['val'].diff(4)  # Assuming quarterly data
                df['pct_change_from_previous_year'] = (df['val'].pct_change(4) * 100)
                
            return df
            
        except Exception as e:
            logger.warning(f"Error calculating period metrics: {str(e)}")
            return df