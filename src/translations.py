import pandas as pd
from file_paths import INPUT_FILES, PROCESSED_FILES
from string import capwords

LANGUAGES = ['Afrikaans', 'Albanian', 'Arabic', 'Armenian', 'Azerbaijani', 'Belarusian', 'Bengali', 'Bulgarian', 'Catalan', 'Chinese', 'Chinese (Traditional)', 'Croatian', 'Czech', 'Danish', 'Dutch', 'Estonian', 'Faroese', 'Finnish', 'French', 'Galician', 'Georgian', 'German', 'Greek', 'Hebrew', 'Hungarian', 'Icelandic', 'Indonesian', 'Italian', 'Japanese', 'Kazakh', 'Korean', 'Latvian', 'Lithuanian', 'Macedonian', 'Marathi', 'Malay', 'Maltese', 'Mongolian', 'Nepali', 'Norwegian', 'Persian', 'Polish', 'Portuguese', 'Romanian', 'Russian', 'Serbian', 'Slovak', 'Slovenian', 'Spanish', 'Swahili', 'Swedish', 'Tajik', 'Thai', 'Turkish', 'Ukrainian', 'Uzbek', 'Vietnamese']

def merge_excel_translations(df):
    """
    Merge translation data from the IOC file.
    """
    df_excel = pd.read_excel(INPUT_FILES["ioc_translations"], dtype="str")
    df = pd.merge(df, df_excel, left_on='Scientific (IOC)', right_on="IOC14.2", how="left")
    
    return df


def merge_csv_translations(df):
    """
    Merge additional translation data from the first version where additional
    translations were scraped from Avibase.
    """
    df_old = pd.read_csv(INPUT_FILES["old_version"], dtype="str")
    
    # Merge on English name first.
    merged_df = pd.merge(df, df_old, left_on='English (Clements)', right_on='PRIMARY_COM_NAME', how="left", suffixes=["", "_old"])
    
    # Update missing values for each specified language column from CSV merge.
    for col in LANGUAGES:
        csv_col = f"{col}_old"
        if col in merged_df.columns and csv_col in merged_df.columns:
            merged_df[col] = merged_df[col].fillna(merged_df[csv_col])
    
    # Merge on Scientific name to pick up any remaining missing translations.
    merged_df = pd.merge(merged_df, df_old, left_on='Scientific (Clements)', right_on='SCI_NAME', how="left", suffixes=["", "_old_2"])
    
    for col in LANGUAGES:
        csv_col_2 = f"{col}_old_2"
        if col in merged_df.columns and csv_col_2 in merged_df.columns:
            merged_df[col] = merged_df[col].fillna(merged_df[csv_col_2])
    
    return merged_df


def merge_translations(base_df):
    """
    Merge translation data from two sources:
      1. Excel file (Multiling IOC 14.2_b.xlsx)
      2. CSV file (Ultimate Birds - old version.csv)
    
    The DataFrame is reindexed to include scientific name and all language columns.
    
    Saves the final CSV to PROCESSED_FILES['translations'].
    """
    print("-------- Merging translations --------")
    pd.set_option("future.no_silent_downcasting", True)
    
    df = base_df[['English (Clements)', 'Scientific (Clements)', 'English (IOC)', 'Scientific (IOC)']].copy()

    # Merge Excel translations.
    df_merged = merge_excel_translations(df)

    # Merge additional CSV translations.
    df_merged = merge_csv_translations(df_merged)

    # Titlelize translations if it the first letter is not capitalized.
    for col in LANGUAGES:
        df_merged[col] = df_merged[col].apply(lambda x: capwords(x) if not pd.isna(x) and x[0].islower() else x)

    final_columns = ['Scientific (Clements)'] + LANGUAGES
    df_merged = df_merged.reindex(columns=final_columns)
    
    df_merged.to_csv(PROCESSED_FILES["translations"], index=False)
