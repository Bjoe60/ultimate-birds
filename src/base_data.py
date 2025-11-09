import pandas as pd
from file_paths import INPUT_FILES, OUTPUT_FILES

def find_matches_on_names(df):
    """Primary matching using direct AviList translations"""
    df_avilist = pd.read_excel(INPUT_FILES['avilist_taxonomy'], usecols=['English_name_AviList', 'Scientific_name', 'AvibaseID']).rename(columns={
        'English_name_AviList': 'English (AviList)',
        'Scientific_name': 'Scientific (AviList)'
    })

    # 1. First try matching on Avibase ID
    df['TAXON_CONCEPT_ID'] = df['TAXON_CONCEPT_ID'].str.replace('avibase-avibase', 'avibase', regex=False)
    df = pd.merge(df, df_avilist, how='left', left_on='TAXON_CONCEPT_ID', right_on='AvibaseID')

    # 2. Then try matching on scientific name
    temp_df = pd.merge(
        df,
        df_avilist[['Scientific (AviList)', 'English (AviList)']],
        left_on='Scientific (Clements)',
        right_on='Scientific (AviList)',
        how='left',
        suffixes=('', '_sci')
    )
    # Update using the merged columns with '_sci' suffix
    df['English (AviList)'] = df['English (AviList)'].combine_first(temp_df['English (AviList)_sci'])
    df['Scientific (AviList)'] = df['Scientific (AviList)'].combine_first(temp_df['Scientific (AviList)_sci'])


    # 3. Then try matching on normalized common name
    df['norm_com_name'] = df['English (Clements)'].str.lower().str.replace('gray', 'grey').str.replace("S'S", "S'").str.replace('-', '').str.replace(' ', '')
    df_avilist['norm_avilist_name'] = df_avilist['English (AviList)'].str.lower().str.replace('-', '').str.replace(' ', '')

    temp_df = pd.merge(
        df[df['English (AviList)'].isna()].reset_index(),
        df_avilist,
        left_on='norm_com_name',
        right_on='norm_avilist_name',
        how='left',
        suffixes=('', '_alt')
    ).set_index('index')

    # Update using the merged columns with '_alt' suffix
    df['English (AviList)'] = df['English (AviList)'].combine_first(temp_df['English (AviList)_alt'])
    df['Scientific (AviList)'] = df['Scientific (AviList)'].combine_first(temp_df['Scientific (AviList)_alt'])

    return df

def get_base_data():
    # Initialize base dataframe
    df = pd.read_csv(INPUT_FILES['ebird_taxonomy'])
    df = df[df['CATEGORY'] == 'species'].rename(columns={
        'PRIMARY_COM_NAME': 'English (Clements)',
        'SCI_NAME': 'Scientific (Clements)'
    })
    df['EBIRD'] = 'https://ebird.org/species/' + df['SPECIES_CODE']
    
    # Find matches between Clements and AviList using scientific and common names
    df = find_matches_on_names(df)

    print(f"AviList names found: {df['English (AviList)'].count()}/{len(df)}")

    df = df[['English (Clements)', 'Scientific (Clements)', 'EBIRD', 'TAXON_ORDER', 
               'ORDER', 'FAMILY', 'TAXON_CONCEPT_ID', 'English (AviList)', 'Scientific (AviList)']]

    df.to_csv(OUTPUT_FILES['base_data'], index=False)
    
    return df