from file_paths import INPUT_FILES, PROCESSED_FILES

def process_mnemonics(df):
    """
    Matching mnemonics by PRIMARY_COM_NAME from a txt file (copied from Warbler Watch)
    """
    print('-------- Getting mnemonics --------')
    df = df[['English (Clements)', 'Scientific (Clements)']].copy()

    with open(INPUT_FILES['mnemonics']) as f:
        birds = f.read().split('\n\n')

    for bird in birds:
        mnemonics = bird.split('\n')
        df.loc[df['English (Clements)'] == mnemonics[0], 'MNEMONIC'] = '<br/>'.join(mnemonics[1:])

    df[['Scientific (Clements)', 'MNEMONIC']].to_csv(PROCESSED_FILES['mnemonics'], index=False)