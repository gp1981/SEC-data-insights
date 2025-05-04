#!/usr/bin/env python3
import click
import logging
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from src.utils.sec_client import SECClient, SECRateLimitError, SECDataError
from src.utils.industry_analyzer import IndustryAnalyzer
from src.examples.process_financial_statements import process_company_financials
from src.examples.analyze_industry import analyze_company_and_peers
from src.config import settings
from click.exceptions import Exit

def setup_logging(verbose: bool):
    """Configure logging"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    level = logging.DEBUG if verbose else logging.INFO
    log_file = log_dir / f"sec_data_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(verbose):
    """SEC Data Insights CLI"""
    setup_logging(verbose)

@cli.command()
@click.argument('cik')
def company_info(cik):
    """Get company information and recent filings"""
    try:
        client = SECClient()
        info = client.get_company_submissions(cik)
        
        click.echo("\nCompany Information:")
        click.echo(f"Name: {info.get('name')}")
        click.echo(f"CIK: {info.get('cik')}")
        if 'tickers' in info:
            click.echo(f"Tickers: {', '.join(info['tickers'])}")
            
    except SECRateLimitError as e:
        click.echo("Rate limit exceeded", err=True)
        raise click.exceptions.Exit(1)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.exceptions.Exit(1)

@cli.command()
@click.argument('cik')
@click.option('--concept', default='Assets')
def get_concept(cik, concept):
    """Get specific financial concept data"""
    try:
        client = SECClient()
        data = client.get_company_concept(cik, 'us-gaap', concept)
        
        for unit, values in data.get('units', {}).items():
            click.echo(f"\nValues in {unit}:")
            for value in values:
                click.echo(f"{value['end']}: {value['val']:,}")
                
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Exit(1)

@cli.command()
@click.argument('cik')
def process_statements(cik):
    """Process company financial statements"""
    from src.examples.process_financial_statements import process_company_financials
    try:
        process_company_financials(cik)
        click.echo("Financial statements processed successfully")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Exit(1)

@cli.command()
@click.argument('cik')
def analyze_peers(cik):
    """Analyze company against industry peers"""
    from src.examples.analyze_industry import analyze_company_and_peers
    try:
        analyze_company_and_peers(cik)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Exit(1)

@cli.command()
@click.argument('metric')
def top_companies(metric):
    """Get top companies by specific metric"""
    from src.utils.industry_analyzer import IndustryAnalyzer
    try:
        analyzer = IndustryAnalyzer()
        rankings = analyzer.get_peer_rankings(metric)
        
        click.echo(f"\nTop companies by {metric}:")
        for _, row in rankings.iterrows():
            click.echo(f"{row['entityName']}: {row['val']:,}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Exit(1)

@cli.command()
def clear_sec_cache():
    """Clear cached SEC API responses"""
    try:
        from src.utils.cache import clear_cache  # Move import here to make mocking work
        count = clear_cache()
        click.echo(f"Cleared {count} cached responses")
    except Exception as e:
        click.echo(f"Error clearing cache: {str(e)}", err=True)
        raise click.Exit(1)  # Use Exit instead of exceptions.Exit

if __name__ == '__main__':
    cli()