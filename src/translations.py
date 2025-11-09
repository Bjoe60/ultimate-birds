import pandas as pd
from file_paths import INPUT_FILES, PROCESSED_FILES
from string import capwords

LANGUAGE_RENAME_MAP = {
    'Chinese, Simple': 'Chinese',
    'Chinese - Mandarin (trad)': 'Chinese (Traditional)',
    'Portuguese, Portugal': 'Portuguese',
    'Nepali (Nepal)': 'Nepali'
}
LANGUAGES_ALL = ['Afrikaans', 'Albanian', 'Arabic', 'Armenian', 'Azerbaijani', 'Belarusian', 'Bengali', 'Bulgarian', 'Catalan', 'Chinese', 'Chinese (Traditional)', 'Croatian', 'Czech', 'Danish', 'Dutch', 'Estonian', 'Faroese', 'Finnish', 'French', 'Galician', 'Georgian', 'German', 'Greek', 'Hebrew', 'Hungarian', 'Icelandic', 'Indonesian', 'Italian', 'Japanese', 'Kazakh', 'Korean', 'Latvian', 'Lithuanian', 'Macedonian', 'Marathi', 'Malay', 'Maltese', 'Mongolian', 'Nepali', 'Norwegian', 'Persian', 'Polish', 'Portuguese', 'Romanian', 'Russian', 'Serbian', 'Slovak', 'Slovenian', 'Spanish', 'Swahili', 'Swedish', 'Tajik', 'Thai', 'Turkish', 'Ukrainian', 'Uzbek', 'Vietnamese']

def merge_ebird_translations(df):
    """
    Merge translation data from the eBird file.
    """
    df_common_names = pd.read_excel(INPUT_FILES["ebird_translations"], dtype="str")
    df_common_names['bio_concept_code'] = df_common_names['bio_concept_code'].str.replace('avibase-avibase', 'avibase', regex=False)

    df = pd.merge(df, df_common_names, left_on='TAXON_CONCEPT_ID', right_on='bio_concept_code', how="left", suffixes=["", "_translations"])
    # Update missing English (AviList) names from translations file (this file is using taxonomy from last year, so prefer existing)
    df['English (AviList)'] = df['English (AviList)'].combine_first(df['English (AviList)_translations'])

    # Rename languages
    df = df.rename(columns=LANGUAGE_RENAME_MAP)
    
    return df


def merge_old_translations(df):
    """
    Merge additional translation data from the first version where additional
    translations were scraped from Avibase.
    """
    df_old = pd.read_csv(INPUT_FILES["old_version"], dtype="str")
    
    # Merge on English name first.
    merged_df = pd.merge(df, df_old, left_on='English (Clements)', right_on='PRIMARY_COM_NAME', how="left", suffixes=["", "_old"])
    
    # Update missing values for each specified language column from CSV merge.
    for col in LANGUAGES_ALL:
        csv_col = f"{col}_old"
        if col in merged_df.columns and csv_col in merged_df.columns:
            merged_df[col] = merged_df[col].fillna(merged_df[csv_col])
    
    # Merge on Scientific name to pick up any remaining missing translations.
    merged_df = pd.merge(merged_df, df_old, left_on='Scientific (Clements)', right_on='SCI_NAME', how="left", suffixes=["", "_old_2"])
    
    for col in LANGUAGES_ALL:
        csv_col_2 = f"{col}_old_2"
        if col in merged_df.columns and csv_col_2 in merged_df.columns:
            merged_df[col] = merged_df[col].fillna(merged_df[csv_col_2])
    
    return merged_df

def overwrite_danish_translations(df):
    """
    Prefer Danish translations from dofbasen, then Navnegruppen, then IOC.
    """
    df_dofbasen = pd.read_csv(INPUT_FILES["danish_translations_dofbasen"], dtype="str", usecols=["Latin", "Artnavn"], sep=";", encoding='ISO-8859-1')
    df_navnegruppen = pd.read_excel(INPUT_FILES["danish_translations_navnegruppen"], dtype="str", sheet_name="DOF-LDF fil", usecols=["Scientific Name", "Dansk Navn"])
    
    df_dofbasen = df_dofbasen.rename(columns={"Latin": "Scientific (AviList)", "Artnavn": "Danish_dofbasen"})
    df_navnegruppen = df_navnegruppen.rename(columns={"Scientific Name": "Scientific (AviList)", "Dansk Navn": "Danish_navnegruppen"})

    df_dofbasen = df_dofbasen.drop_duplicates(subset=["Scientific (AviList)"], keep="first")
    df_navnegruppen = df_navnegruppen.drop_duplicates(subset=["Scientific (AviList)"], keep="first")

    df = pd.merge(df, df_dofbasen, on="Scientific (AviList)", how="left")
    df = pd.merge(df, df_navnegruppen, on="Scientific (AviList)", how="left")

    df["Danish"] = df.apply(
        lambda row: row["Danish_dofbasen"] if pd.notna(row["Danish_dofbasen"]) else row["Danish_navnegruppen"] if pd.notna(row["Danish_navnegruppen"]) else row["Danish"], axis=1
    )
    return df

def merge_translations(base_df):
    """
    Merge translation data from four sources:
      1. eBird common names (eBird_Taxonomy_v2024_5-tab_5Sep2025a.xlsx)
      2. Old version (Ultimate Birds - old version.csv)
      3. Danish translations (dofbasen.csv)
      4. Danish translations (navnegruppen.xlsx)
    
    The DataFrame is reindexed to include scientific name and all language columns.
    
    Saves the final CSV to PROCESSED_FILES['translations'].
    """
    print("-------- Merging translations --------")

    df = base_df[['English (Clements)', 'Scientific (Clements)', 'English (AviList)', 'Scientific (AviList)', 'TAXON_CONCEPT_ID']].copy()

    # Merge Excel translations.
    df_merged = merge_ebird_translations(df)

    # # Merge additional translations from an older version.
    df_merged = merge_old_translations(df_merged)

    df_merged = overwrite_danish_translations(df_merged)

    # # Titlelize translations if it the first letter is not capitalized.
    for col in LANGUAGES_ALL:
        df_merged[col] = df_merged[col].apply(lambda x: capwords(x) if not pd.isna(x) and x[0].islower() else x)

    final_columns = ['Scientific (Clements)'] + LANGUAGES_ALL
    df_merged = df_merged.reindex(columns=final_columns)
    
    df_merged.to_csv(PROCESSED_FILES["translations"], index=False, encoding="utf-8")
