import pandas as pd
from file_paths import INPUT_FILES, OUTPUT_FILES, IOC_COLUMN


if __name__ == '__main__':
    df_clements_vs_ioc = pd.read_excel(INPUT_FILES['clements_to_ioc']).rename(columns={
        'IOC scientific name': 'Scientific (IOC)',
    })
    df_dofbasen = pd.read_csv(INPUT_FILES['danish_translations_dofbasen'], sep=";", usecols=['Latin']).rename(columns={
        'Latin': 'Scientific (IOC)',
    })

    df_clements_vs_ioc = pd.merge(df_clements_vs_ioc, df_dofbasen, on='Scientific (IOC)', how='inner')
    df_clements_vs_ioc = df_clements_vs_ioc[df_clements_vs_ioc['Degree of match'] == 0]
    
    df_clements_vs_ioc.to_csv(OUTPUT_FILES['clements_vs_ioc_danish'], index=False)