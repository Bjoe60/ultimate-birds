import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.file_paths import OUTPUT_FILES

def test_empty_values():
    """
    Test if any of the specified columns contain empty values.
    """
    columns = {'English', 'Scientific', 'eBird URL', 'Taxonomic order', 'Order', 'Family', 'Avibase URL', 'Conservation status'}
    df = pd.read_csv(OUTPUT_FILES['output_header'], dtype=str)
    
    for column in columns:
        assert not df[column].isnull().values.any(), f"Empty values found in column: {column}"

def test_duplicate_values():
    """
    Test if any of the specified columns contain duplicate values.
    """
    columns = {'English', 'Scientific', 'eBird URL', 'Taxonomic order', 'Avibase URL'}
    df = pd.read_csv(OUTPUT_FILES['output_header'], dtype=str)

    for column in columns:
        assert not df[column].dropna().duplicated().any(), f"Duplicate values found in column: {column}"