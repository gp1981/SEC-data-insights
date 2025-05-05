import pandas as pd
from typing import Dict, List, Any
from pathlib import Path
import json
import logging

def facts_to_dataframe(facts_data: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
    """
    Convert SEC facts JSON data into pandas DataFrames
    
    Args:
        facts_data: Raw JSON data from SEC API
        
    Returns:
        Dict mapping taxonomy_concept to DataFrame
    """
    dataframes = {}
    
    # Process each taxonomy
    for taxonomy, concepts in facts_data.get('facts', {}).items():
        # Process each concept
        for concept_name, concept_data in concepts.items():
            # Skip if no units data
            if not concept_data.get('units'):
                continue
                
            # Process each unit type
            for unit_type, values in concept_data['units'].items():
                # Create DataFrame for this concept
                df = pd.DataFrame(values)
                
                # Add metadata columns
                df['taxonomy'] = taxonomy
                df['concept'] = concept_name
                df['unit'] = unit_type
                df['label'] = concept_data.get('label', '')
                
                # Convert date columns
                if 'end' in df.columns:
                    df['end'] = pd.to_datetime(df['end'])
                if 'filed' in df.columns:
                    df['filed'] = pd.to_datetime(df['filed'])
                    
                # Store with unique key
                key = f"{taxonomy}_{concept_name}_{unit_type}"
                dataframes[key] = df
    
    # Add debug logging
    logger = logging.getLogger(__name__)
    logger.debug(f"Created {len(dataframes)} DataFrames in memory")
    for name, df in dataframes.items():
        logger.debug(f"DataFrame {name}: {df.shape} shape, Memory usage: {df.memory_usage().sum() / 1024**2:.2f} MB")
    
    return dataframes

def load_and_process_facts(file_path: str) -> Dict[str, pd.DataFrame]:
    """
    Load facts from JSON file and convert to DataFrames
    
    Args:
        file_path: Path to JSON file containing SEC facts
        
    Returns:
        Dict mapping taxonomy_concept to DataFrame
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Facts file not found: {file_path}")
        
    with path.open('r') as f:
        facts_data = json.load(f)
        
    return facts_to_dataframe(facts_data)