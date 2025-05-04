from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# SEC API Configuration
SEC_API_BASE_URL = "https://data.sec.gov"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions"
SEC_USER_AGENT = os.getenv('SEC_USER_AGENT', 'Company Research Tool research@example.com')
SEC_RATE_LIMIT_DELAY = float(os.getenv('SEC_RATE_LIMIT_DELAY', '0.1'))  # 10 requests per second
SEC_MAX_RETRIES = int(os.getenv('SEC_MAX_RETRIES', '3'))
SEC_RETRY_DELAY = int(os.getenv('SEC_RETRY_DELAY', '1'))

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///sec_filings.db')
ECHO_SQL = os.getenv('ECHO_SQL', 'false').lower() == 'true'

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Data Processing Configuration
OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', 'financial_statements'))
CACHE_DIR = Path(os.getenv('CACHE_DIR', '.cache'))

# Create required directories
OUTPUT_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)