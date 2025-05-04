# SEC Data Insights

A comprehensive Python CLI tool for retrieving, analyzing, and visualizing financial data from the SEC's EDGAR database. This tool helps investors, analysts, and researchers access and process financial information from publicly traded companies.

## Overview

SEC Data Insights provides automated access to:
- Company financial statements and filings
- XBRL-formatted financial data
- Industry peer comparisons
- Key financial metrics and ratios
- Historical financial performance

## Features

### Data Retrieval
- Fetch company submissions and filings
- Access detailed XBRL financial data
- Download quarterly and annual reports
- Retrieve specific financial concepts
- Support for both US-GAAP and IFRS taxonomies

### Analysis Tools
- Industry peer comparison
- Financial ratio calculations
- Time series analysis
- Performance benchmarking
- Custom metric definitions

### Performance
- Intelligent caching system
- Rate limit handling
- Parallel processing capabilities
- Efficient data storage
- Memory optimization

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Git (for installation)

### Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SEC-data-insights.git
```

2. Navigate to project directory:
```bash
cd SEC-data-insights
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Usage

### Command Line Interface

#### Company Information
```bash
# Get basic company info
python -m src.cli company-info 0000028917

# Output includes:
# - Company name
# - CIK number
# - Industry classification
# - Recent filings
```

#### Financial Concepts
```bash
# Get specific financial metrics
python -m src.cli get-concept 0000028917 --concept Assets
python -m src.cli get-concept 0000028917 --concept Revenue --taxonomy us-gaap

# Supported concepts:
# - Assets, Liabilities, Equity
# - Revenue, NetIncome, OperatingIncome
# - And many more US-GAAP/IFRS concepts
```

#### Industry Analysis
```bash
# Analyze peer companies
python -m src.cli analyze-peers 0000028917 --metric Revenue --year 2023 --quarter 4

# Compare multiple metrics
python -m src.cli analyze-peers 0000028917 --metrics Revenue,NetIncome,Assets
```

#### Cache Management
```bash
# Clear all cached data
python -m src.cli clear-sec-cache

# Clear specific cache patterns
python -m src.cli clear-sec-cache --pattern "company-info"
```

### API Integration

The tool uses several SEC EDGAR API endpoints:

#### Company Submissions
```
https://data.sec.gov/submissions/CIK{cik}.json
- Returns company metadata and filing history
- Includes CIK, name, fiscal year end
- Lists recent and older filings
```

#### Company Concepts
```
https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/{taxonomy}/{concept}.json
- Retrieves specific financial concepts
- Supports multiple taxonomies
- Returns time series data
```

#### Company Facts
```
https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json
- Provides all available financial facts
- Includes detailed context information
- Supports different units of measure
```

## Interface Options

### 1. Python CLI (Current Implementation)
```bash
python -m src.cli company-info 0000028917
```

### 2. Python API Usage
Import and use the modules directly in your Python code:

```python
from src.utils.sec_client import SECClient
from src.utils.industry_analyzer import IndustryAnalyzer

# Initialize client
client = SECClient()

# Get company data
company_data = client.get_company_submissions("0000028917")

# Analyze industry peers
analyzer = IndustryAnalyzer()
peer_analysis = analyzer.get_peer_rankings(
    metric="Revenue",
    year=2023,
    quarter=4
)
```

### 3. REST API Server (Future Implementation)
Run as a web service using FastAPI:

```python
from fastapi import FastAPI
from src.utils.sec_client import SECClient

app = FastAPI()
client = SECClient()

@app.get("/company/{cik}")
async def get_company_info(cik: str):
    return client.get_company_submissions(cik)

@app.get("/concept/{cik}/{concept}")
async def get_concept(cik: str, concept: str):
    return client.get_company_concept(cik, "us-gaap", concept)
```

Start the server:
```bash
uvicorn src.api.server:app --reload
```

Access via HTTP:
```bash
curl http://localhost:8000/company/0000028917
curl http://localhost:8000/concept/0000028917/Assets
```

### 4. GUI Application (Potential Extension)
A desktop application could be built using:
- PyQt/PySide
- Tkinter
- wxPython
- Electron (for cross-platform desktop app)

### 5. Jupyter Notebook Integration
Interactive analysis in Jupyter notebooks:

```python
from src.utils.sec_client import SECClient
import pandas as pd
import matplotlib.pyplot as plt

# Get financial data
client = SECClient()
data = client.get_company_concept("0000028917", "us-gaap", "Revenue")

# Create DataFrame
df = pd.DataFrame(data["units"]["USD"])

# Plot revenue over time
plt.figure(figsize=(12, 6))
plt.plot(df["end"], df["val"])
plt.title("Revenue Over Time")
plt.show()
```

## Project Structure

```
src/
├── api/                 # API interface layer
│   ├── endpoints.py    # API endpoint definitions
│   └── handlers.py     # Request/response handlers
├── utils/              # Utility functions
│   ├── cache.py       # Caching system
│   ├── sec_client.py  # SEC API client
│   └── industry_analyzer.py # Industry analysis
├── processors/         # Data processors
│   ├── xbrl.py       # XBRL data processor
│   └── financial.py   # Financial calculations
├── examples/           # Usage examples
└── cli.py             # Command line interface

tests/                 # Test suite
├── unit/             # Unit tests
├── integration/      # Integration tests
└── fixtures/         # Test fixtures
```

## Testing

### Running Tests
```bash
# Run all tests
pytest --verbose

# Run specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v

# Run with coverage report
pytest --cov=src --cov-report=term-missing
```

### Test Categories
- Unit Tests: Individual component testing
- Integration Tests: End-to-end functionality
- Performance Tests: Response times and caching
- Error Handling: Edge cases and failures

## Configuration

### Environment Variables
```bash
# API Configuration
SEC_API_KEY=your_api_key        # Your SEC API key
SEC_API_EMAIL=email@domain.com  # Required by SEC

# Performance Settings
CACHE_DIR=.cache               # Cache directory location
RATE_LIMIT_DELAY=0.1          # Delay between requests
MAX_RETRIES=3                 # Request retry attempts

# Output Settings
LOG_LEVEL=INFO                # Logging detail level
OUTPUT_FORMAT=json            # Data output format
```

## Rate Limiting

The SEC EDGAR API enforces rate limits:
- 10 requests per second maximum
- Requires valid SEC API key
- Automatic retry on rate limit errors
- Configurable delay between requests

## Contributing

1. Fork the repository
2. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```
3. Make your changes
4. Run tests:
```bash
pytest
```
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Use type hints
- Include docstrings

## License

[Add your license information here]

## Acknowledgments

- SEC EDGAR system documentation
- XBRL US working group
- Financial statement taxonomy guides
