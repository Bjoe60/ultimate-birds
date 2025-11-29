import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.file_paths import OUTPUT_FILES

def test_possibly_wrong_mapped():
    """
    Test to identify potentially incorrect mappings between AviList and Clements scientific names in a dataset.
    This function reads a CSV file containing bird data, extracts the scientific names according to Clements taxonomy,
    and iterates through each row to check if the AviList scientific name is present in the Clements scientific names set.
    If a mismatch is found (i.e., the AviList scientific name is in the Clements set but does not match the Clements name
    for that row), an assertion error is raised with a message indicating the mismatch.
    Raises:
        AssertionError: If an AviList scientific name is found in the Clements scientific names set but does not match
                        the Clements scientific name for that row.
    """

    df = pd.read_csv(OUTPUT_FILES['base_data'], dtype=str)

    clements_scientific_names = set(df['Scientific (Clements)'].dropna())

    for index, row in df.iterrows():
        avilist_scientific_name = row['Scientific (AviList)']

        if pd.notna(avilist_scientific_name):
            assert not (avilist_scientific_name in clements_scientific_names and avilist_scientific_name != row['Scientific (Clements)']), f"Mismatch found: {row['Scientific (AviList)']}"
