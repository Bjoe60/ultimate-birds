import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.file_paths import OUTPUT_FILES

def test_duplicates():
    """
    Test to identify duplicated values in the dataset.
    This function reads a CSV file containing bird data and checks for duplicated values in the specified columns.
    """
    columns = ['English (Clements)', 'Scientific (Clements)', 'English (IOC)', 'Scientific (IOC)']
    for column in columns:
        df = pd.read_csv(OUTPUT_FILES['base_data'], dtype=str)
        df = df[df.duplicated(subset=[column], keep=False)].drop_duplicates(subset=[column])
        df = df.sort_values(column)
        for i in df[column]:
            assert pd.isna(i), f"Found {i} in {column}."