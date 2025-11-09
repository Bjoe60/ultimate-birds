import pandas as pd
from file_paths import INPUT_FILES, OUTPUT_FILES


if __name__ == '__main__':
    df_clements = pd.read_csv(INPUT_FILES['ebird_taxonomy'], usecols=['TAXON_CONCEPT_ID', 'CATEGORY', 'SCI_NAME', 'SPECIES_CODE'])
    df_clements = df_clements[df_clements['CATEGORY'] == 'species']
    df_clements['TAXON_CONCEPT_ID'] = df_clements['TAXON_CONCEPT_ID'].str.replace('avibase-avibase', 'avibase', regex=False)

    df_avilist = pd.read_excel(INPUT_FILES['avilist_taxonomy'], usecols=['AvibaseID', 'Scientific_name', 'English_name_AviList'])
    
    df_clements_vs_avilist = pd.merge(df_clements, df_avilist, how='left', left_on='TAXON_CONCEPT_ID', right_on='AvibaseID')
    df_clements_vs_avilist = df_clements_vs_avilist[df_clements_vs_avilist['SCI_NAME'] != df_clements_vs_avilist['Scientific_name']]
    
    # df_dofbasen = pd.read_csv(INPUT_FILES['danish_translations_dofbasen'], sep=";", usecols=['Latin', 'Artnavn'], encoding='ISO-8859-1')

    # df_clements_vs_avilist = pd.merge(
    #     df_clements_vs_avilist,
    #     df_dofbasen,
    #     how='inner',
    #     left_on='SCI_NAME',
    #     right_on='Latin'
    # )

    df_clements_vs_avilist.to_csv(OUTPUT_FILES['clements_vs_avilist'], index=False)