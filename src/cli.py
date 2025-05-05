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
from src.utils.data_processor import facts_to_dataframe, load_and_process_facts

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
@click.option('--concept', default='Assets', help='Financial concept to retrieve (e.g., Assets, Revenue)')
@click.option('--taxonomy', default='us-gaap', type=click.Choice(['us-gaap', 'ifrs']), help='Taxonomy to use')
def get_concept(cik, concept, taxonomy):
    """Get specific financial concept data"""
    try:
        client = SECClient()
        data = client.get_company_concept(cik, taxonomy, concept)
        
        if not data.get('units'):
            click.echo(f"No data found for {concept} using {taxonomy} taxonomy", err=True)
            raise click.Exit(1)
            
        for unit, values in data['units'].items():
            click.echo(f"\nValues in {unit}:")
            for value in values:
                click.echo(f"{value['end']}: {value['val']:,}")
                
    except SECRateLimitError:
        click.echo("Rate limit exceeded", err=True)
        raise click.Exit(1)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Exit(1)

@cli.command()
@click.argument('cik')
@click.option('--output', '-o', type=click.Path(), help='Output file path for JSON data')
def get_company_facts(cik, output):
    """Get all XBRL facts for a company"""
    try:
        client = SECClient()
        facts = client.get_company_facts(cik)
        
        if not facts:
            click.echo("No facts found for company", err=True)
            raise click.Exit(1)
            
        # Save to file if output path provided
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open('w') as f:
                json.dump(facts, f, indent=2)
            click.echo(f"\nSaved facts data to {output}")
            
        # Display summary of available fact categories
        click.echo("\nAvailable Fact Categories:")
        for taxonomy, concepts in facts.get('facts', {}).items():
            concept_count = len(concepts)
            click.echo(f"{taxonomy}: {concept_count} concepts")
            
            # Display sample of concepts
            if concept_count > 0:
                sample_concepts = list(concepts.keys())[:5]
                click.echo("Sample concepts: " + ", ".join(sample_concepts))
            click.echo()
                
    except SECRateLimitError:
        click.echo("Rate limit exceeded", err=True)
        raise click.Exit(1)
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

@cli.command()
@click.argument('cik')
@click.option('--output', '-o', type=click.Path(), help='Output file path for processed data (optional)')
@click.option('--format', 'output_format', type=click.Choice(['csv', 'excel']), default='csv')
@click.option('--inspect/--no-inspect', default=True, help='Show detailed DataFrame information')
def process_facts(cik, output, output_format, inspect):
    """Process company facts into DataFrame and optionally save to file"""
    try:
        # Get facts data
        client = SECClient()
        facts = client.get_company_facts(cik)
        
        # Convert to DataFrames
        dataframes = facts_to_dataframe(facts)
        
        if not dataframes:
            click.echo("No processable facts found", err=True)
            raise click.Exit(1)
            
        # Display DataFrame information
        if inspect:
            click.echo("\nDataFrame Information:")
            for name, df in dataframes.items():
                click.echo(f"\n{'-'*50}")
                click.echo(f"DataFrame: {name}")
                click.echo(f"Shape: {df.shape}")
                click.echo("\nColumns:")
                for col in df.columns:
                    dtype = df[col].dtype
                    n_null = df[col].isna().sum()
                    click.echo(f"- {col}: {dtype} ({n_null} null values)")
                click.echo("\nSample Data:")
                click.echo(df.head().to_string())
        
        # Save to file if output path provided
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if output_format == 'csv':
                for name, df in dataframes.items():
                    csv_path = output_path.parent / f"{output_path.stem}_{name}.csv"
                    df.to_csv(csv_path, index=False)
                click.echo(f"\nSaved {len(dataframes)} CSV files to {output_path.parent}")
            else:
                with pd.ExcelWriter(output_path) as writer:
                    for name, df in dataframes.items():
                        df.to_excel(writer, sheet_name=name[:31], index=False)
                click.echo(f"\nSaved data to Excel file: {output_path}")
            
    except Exception as e:
        click.echo(f"Error processing facts: {str(e)}", err=True)
        raise click.Exit(1)

if __name__ == '__main__':
    cli()