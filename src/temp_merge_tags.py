import pandas as pd
from file_paths import PROCESSED_FILES

df_full = pd.read_csv('data/processed/avibase_FULL.csv')
df_wpa = pd.read_csv('data/processed/avibase_WPA.csv')

# Append blank space + 'TAGS' from WPA to 'TAGS' on full dataset (vectorized)
wpa_tags = df_wpa.set_index('Scientific (Clements)')['TAGS']
df_full['TAGS'] = (
        df_full['TAGS'].fillna('').astype(str) + ' ' + df_full['Scientific (Clements)'].map(wpa_tags).fillna('')
    ).str.strip()

df_full.to_csv(PROCESSED_FILES['avibase'], index=False)