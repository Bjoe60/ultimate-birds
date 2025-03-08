import pandas as pd
from file_paths import INPUT_FILES, OUTPUT_FILES

def match_ioc(df):
    """Primary matching using direct IOC translations"""
    df_ioc = pd.read_excel(INPUT_FILES['ioc_translations'], usecols=['English', 'IOC14.2']).rename(columns={
        'English': 'English (IOC)',
        'IOC14.2': 'Scientific (IOC)'
    })
    
    # 1. First try direct scientific name match
    df = pd.merge(
        df,
        df_ioc[['Scientific (IOC)', 'English (IOC)']],
        left_on='Scientific (Clements)',
        right_on='Scientific (IOC)',
        how='left',
        suffixes=('', '_sci')
    )
    
    # 2. Then try normalized common name match
    df['norm_com_name'] = df['English (Clements)'].str.lower().str.replace('gray', 'grey').str.replace("S'S", "S'").str.replace('-', '').str.replace(' ', '')
    df_ioc['norm_ioc_name'] = df_ioc['English (IOC)'].str.lower().str.replace('-', '').str.replace(' ', '')
    
    temp_df = pd.merge(
        df[df['English (IOC)'].isna()].reset_index(),
        df_ioc,
        left_on='norm_com_name',
        right_on='norm_ioc_name',
        how='left',
        suffixes=('', '_alt')
    ).set_index('index')

    # Update using the merged columns with '_alt' suffix
    df['English (IOC)'] = df['English (IOC)'].combine_first(temp_df['English (IOC)_alt'])
    df['Scientific (IOC)'] = df['Scientific (IOC)'].combine_first(temp_df['Scientific (IOC)_alt'])
    
    return df

def map_clements_ioc(df):
    """
    Fallback mapping using Clements-IOC relationships
    However, this file is outdated so a match on both common
    and scientific names is used.
    The file also contains typos for a few species.
    """
    df_clements_ioc = pd.read_excel(INPUT_FILES['clements_to_ioc']).rename(columns={
        'IOC common name': 'English (IOC)',
        'IOC scientific name': 'Scientific (IOC)',
        'Clements common name': 'English (Clements)',
        'Clements scientific name': 'Scientific (Clements)'
    })
    
    # Merge using Clements scientific names as backup
    df = pd.merge(
        df,
        df_clements_ioc,
        on='Scientific (Clements)',
        how='left',
        suffixes=('', '_clements')
    )
    
    # Fill missing IOC data from Clements mappings
    df['English (IOC)'] = df['English (IOC)'].combine_first(df['English (IOC)_clements'])
    df['Scientific (IOC)'] = df['Scientific (IOC)'].combine_first(df['Scientific (IOC)_clements'])

    # --- Second Merge: Using English (IOC) / IOC common names for remaining missing ---
    temp_df_common_name_merge = pd.merge(
        df[df['English (IOC)'].isna()].reset_index(), # Use only rows with missing 'English (IOC)'
        df_clements_ioc,
        on='English (Clements)',
        how='left',
        suffixes=('', '_common') # Suffix for columns from this common name merge
    ).set_index('index') # Reset index to align with original df for update

    # Update missing 'English (IOC)' and 'Scientific (IOC)' from common name merge results
    df.loc[temp_df_common_name_merge.index, 'English (IOC)'] = df['English (IOC)'].combine_first(temp_df_common_name_merge['English (IOC)_common'])
    df.loc[temp_df_common_name_merge.index, 'Scientific (IOC)'] = df['Scientific (IOC)'].combine_first(temp_df_common_name_merge['Scientific (IOC)_common'])
    
    return df

def get_base_data():
    # Initialize base dataframe
    df = pd.read_csv(INPUT_FILES['ebird_taxonomy'])
    df = df[df['CATEGORY'] == 'species'].rename(columns={
        'PRIMARY_COM_NAME': 'English (Clements)',
        'SCI_NAME': 'Scientific (Clements)'
    })
    df['EBIRD'] = 'https://ebird.org/species/' + df['SPECIES_CODE']
    
    # First try direct IOC matches
    df = match_ioc(df)
    
    # Then fill gaps with Clements-IOC mappings
    df = map_clements_ioc(df)
    
    print(f"IOC names found: {df['English (IOC)'].count()}/{len(df)}")

    df.to_csv(OUTPUT_FILES['base_data'], index=False)
    
    return df[['English (Clements)', 'Scientific (Clements)', 'EBIRD', 'TAXON_ORDER', 
               'ORDER', 'FAMILY', 'English (IOC)', 'Scientific (IOC)']]