import requests
import time
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from enum import Enum
from src.config import settings
from src.utils.cache import cache_sec_response

logger = logging.getLogger(__name__)

class SECRateLimitError(Exception):
    """Exception raised when SEC API rate limit is exceeded"""
    pass

class SECDataError(Exception):
    """Exception raised for SEC data retrieval or format errors"""
    pass

class Period(Enum):
    """Enumeration for SEC frame period types"""
    ANNUAL = "CY"
    QUARTERLY = "CYQ"
    INSTANT = "CYI"

class SECClient:
    """Enhanced SEC API client with support for all SEC data endpoints"""
    
    def __init__(self):
        self.base_url = "https://data.sec.gov"
        self.submissions_url = f"{self.base_url}/submissions"
        self.api_url = f"{self.base_url}/api/xbrl"
        self.headers = {
            'User-Agent': settings.SEC_USER_AGENT,
            'Accept': 'application/json',
        }
        self.last_request_time = 0
        self.min_request_interval = settings.SEC_RATE_LIMIT_DELAY
        self.max_retries = settings.SEC_MAX_RETRIES
        self.retry_delay = settings.SEC_RETRY_DELAY

    def _rate_limit(self):
        """Implements rate limiting for SEC API requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        self.last_request_time = time.time()

    def _make_request(self, url: str, method: str = 'GET') -> Dict[str, Any]:
        """
        Makes a rate-limited request to the SEC API with retries
        
        Args:
            url: The URL to request
            method: HTTP method to use
            
        Returns:
            Dict containing the JSON response
            
        Raises:
            SECRateLimitError: If rate limit is exceeded
            SECDataError: If data retrieval fails
        """
        for attempt in range(self.max_retries):
            try:
                self._rate_limit()
                response = requests.request(method, url, headers=self.headers)
                
                if response.status_code == 429:  # Too Many Requests
                    raise SECRateLimitError("SEC API rate limit exceeded")
                
                response.raise_for_status()
                return response.json()
                
            except SECRateLimitError:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.retry_delay * (attempt + 1))
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise SECDataError(f"Failed to retrieve SEC data: {str(e)}")
                logger.warning(f"Request failed (attempt {attempt + 1}): {str(e)}")
                time.sleep(self.retry_delay)

    def _validate_cik(self, cik: str) -> str:
        """
        Validates and formats CIK number
        
        Args:
            cik: Company CIK number
            
        Returns:
            Formatted 10-digit CIK
            
        Raises:
            ValueError: If CIK is invalid
        """
        cik_str = str(cik).strip().lstrip('0')
        if not cik_str.isdigit():
            raise ValueError("CIK must contain only digits")
        return cik_str.zfill(10)

    @cache_sec_response(expires_after=timedelta(days=1))
    def get_company_list(self) -> Dict[str, Any]:
        """
        Retrieves list of all companies from SEC.
        Cached for 24 hours.
        
        Returns:
            Dict containing company tickers and metadata
            
        Raises:
            SECRateLimitError: If rate limit is exceeded
            SECDataError: If data retrieval fails
        """
        url = f"{self.base_url}/files/company_tickers.json"
        return self._make_request(url)

    @cache_sec_response(expires_after=timedelta(hours=6))
    def get_company_submissions(self, cik: str) -> Dict[str, Any]:
        """
        Retrieves company submission history including metadata and recent filings.
        Cached for 6 hours.
        
        Args:
            cik: Company CIK number
            
        Returns:
            Dict containing company metadata and filing history
            
        Raises:
            SECRateLimitError: If rate limit is exceeded
            SECDataError: If data retrieval fails
            ValueError: If CIK is invalid
        """
        cik = self._validate_cik(cik)
        url = f"{self.submissions_url}/CIK{cik}.json"
        return self._make_request(url)

    @cache_sec_response(expires_after=timedelta(days=7))
    def get_company_facts(self, cik: str) -> Dict[str, Any]:
        """
        Retrieves all XBRL facts for a company across all filings.
        Cached for 7 days as historical data changes infrequently.
        
        Args:
            cik: Company CIK number
            
        Returns:
            Dict containing all company XBRL facts
            
        Raises:
            SECRateLimitError: If rate limit is exceeded
            SECDataError: If data retrieval fails
            ValueError: If CIK is invalid
        """
        cik = self._validate_cik(cik)
        url = f"{self.api_url}/companyfacts/CIK{cik}.json"
        return self._make_request(url)

    def get_company_facts(self, cik: str) -> dict:
        """
        Get all XBRL facts for a company
        
        Args:
            cik: Company CIK number (will be zero-padded to 10 digits)
            
        Returns:
            dict: Complete company facts data
        """
        cik = self._validate_cik(cik)
        url = f"{self.api_url}/companyfacts/CIK{cik}.json"
        
        return self._make_request(url)

    @cache_sec_response(expires_after=timedelta(days=7))
    def get_company_concept(self, cik: str, taxonomy: str, tag: str) -> Dict[str, Any]:
        """
        Retrieves a specific XBRL concept/tag data for a company.
        Cached for 7 days as concept data changes infrequently.
        
        Args:
            cik: Company CIK number
            taxonomy: The taxonomy to query (e.g., "us-gaap", "ifrs-full", "dei", "srt")
            tag: The concept tag to retrieve (e.g., "Assets", "AccountsPayableCurrent")
            
        Returns:
            Dict containing concept data across all filings
            
        Raises:
            SECRateLimitError: If rate limit is exceeded
            SECDataError: If data retrieval fails
            ValueError: If CIK is invalid
        """
        cik = self._validate_cik(cik)
        url = f"{self.api_url}/companyconcept/CIK{cik}/{taxonomy}/{tag}.json"
        return self._make_request(url)

    @cache_sec_response(expires_after=timedelta(days=30))
    def get_frames(self, 
                  taxonomy: str,
                  tag: str,
                  unit: str,
                  year: int,
                  quarter: Optional[int] = None,
                  instantaneous: bool = False
                  ) -> Dict[str, Any]:
        """
        Retrieves aggregated data for a specific concept across all companies
        for a given time period. Cached for 30 days as historical frame data
        is effectively immutable.
        
        Args:
            taxonomy: The taxonomy (e.g., "us-gaap", "ifrs-full")
            tag: The concept tag (e.g., "Assets", "AccountsPayableCurrent")
            unit: The unit of measure (e.g., "USD", "USD-per-shares")
            year: The year (YYYY format)
            quarter: Optional quarter number (1-4)
            instantaneous: Whether to retrieve point-in-time data
            
        Returns:
            Dict containing aggregated data across companies
            
        Raises:
            SECRateLimitError: If rate limit is exceeded
            SECDataError: If data retrieval fails
            ValueError: If parameters are invalid
        """
        if quarter and not 1 <= quarter <= 4:
            raise ValueError("Quarter must be between 1 and 4")

        # Construct period string
        if quarter:
            period = f"CY{year}Q{quarter}"
            if instantaneous:
                period += "I"
        else:
            period = f"CY{year}"

        url = f"{self.api_url}/frames/{taxonomy}/{tag}/{unit}/{period}.json"
        return self._make_request(url)