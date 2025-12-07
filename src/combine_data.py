from file_paths import INPUT_FILES, PROCESSED_FILES, OUTPUT_FILES
import pandas as pd
import csv

ALL_COUNTRIES = {"Zimbabwe", "Zambia", "Yemen", "Western-Sahara", "Wallis-and-Futuna-Islands", "Vietnam", "Venezuela", "Vatican", "Vanuatu", "Uzbekistan", "US-Minor-Outlying-Islands", "Uruguay", "United-States-Virgin-Islands", "United-States", "United-Kingdom", "United-Arab-Emirates", "Ukraine", "Uganda", "Tuvalu", "Turks-and-Caicos-Islands", "Turkmenistan", "Turkey", "Tunisia", "Trinidad-and-Tobago", "Trinidad-and-Tobago", "Tonga", "Tokelau", "Togo", "Timor-Leste", "Thailand", "Tanzania", "Tajikistan", "Taiwan", "Syria", "Switzerland", "Sweden", "Suriname", "Sudan", "St.Vincent-and-Grenadines", "Sri-Lanka", "Spain", "South-Sudan", "South-Korea", "South-Georgia-and-South-Sandwich-Islands", "South-Africa", "Somalia", "Solomon-Islands", "Slovenia", "Slovakia", "Sint-Maarten", "Singapore", "Sierra-Leone", "Seychelles", "Serbia", "Senegal", "Saudi-Arabia", "Sao-Tome-and-Principe", "San-Marino", "Samoa", "Saint-Pierre-et-Miquelon", "Saint-Martin", "Saint-Lucia", "Saint-Kitts-and-Nevis", "Saint-Helena,-Ascension-and-Tristan-da-Cunha", "Saint-Barthélemy", "Réunion", "Rwanda", "Russian-Federation", "Romania", "Republic-of-the-Congo", "Qatar", "Puerto-Rico", "Portugal", "Poland", "Pitcairn", "Philippines", "Peru", "Paraguay", "Papua-New-Guinea", "Panama", "Palestine", "Palau", "Pakistan", "Oman", "Norway", "Northern-Marianas", "North-Macedonia", "North-Korea", "Niue", "Nigeria", "Niger", "Nicaragua", "New-Zealand", "New-Caledonia", "Netherlands", "Nepal", "Nauru", "Namibia", "Myanmar", "Mozambique", "Morocco", "Montserrat", "Montenegro", "Mongolia", "Monaco", "Moldova", "Mexico", "Mayotte", "Mauritius", "Mauritania", "Martinique", "Marshall-Islands", "Malta", "Mali", "Maldives", "Malaysia", "Malawi", "Madagascar", "Macau", "Luxembourg", "Lithuania", "Liechtenstein", "Libya", "Liberia", "Lesotho", "Lebanon", "Latvia", "Laos", "Kyrgyzstan", "Kuwait", "Kosovo", "Kiribati", "Kenya", "Kazakhstan", "Jordan", "Japan", "Jamaica", "Italy", "Israel", "Ireland", "Iraq", "Iran", "Indonesia", "India", "Iceland", "Hungary", "Hong-Kong", "Honduras", "Heard-and-McDonald-Islands", "Haiti", "Guyana", "Guinea-Bissau", "Guinea", "Guatemala", "Guam", "Guadeloupe", "Grenada", "Greenland", "Greece", "Gibraltar", "Ghana", "Germany", "Georgia", "Gambia", "Gabon", "French-Southern-Territory", "French-Polynesia", "French-Guiana", "France", "Finland", "Fiji", "Faroe-Islands", "Federated-States-of-Micronesia", "Falkland-Islands-(Malvinas)", "Ethiopia", "Eswatini", "Estonia", "Eritrea", "Equatorial-Guinea", "El-Salvador", "Egypt", "Ecuador", "Dominican-Republic", "Dominica", "Djibouti", "Denmark", "Democratic-Republic-of-the-Congo", "Côte-d'Ivoire", "Czechia", "Cyprus", "Curaçao", "Cuba", "Croatia", "Costa-Rica", "Cook-Islands", "Comoros", "Colombia", "China", "Chile", "Chad", "Central-African-Republic", "Cayman-Islands", "Cape-Verde", "Canada", "Cameroon", "Cambodia", "Burundi", "Burkina-Faso", "Bulgaria", "Brunei-Darussalam", "British-Virgin-Islands", "British-Indian-Ocean-Territory", "British-Antarctic-Territory", "Brazil", "Bouvet-Island", "Botswana", "Bosnia-and-Herzegovina", "Bonaire,-Sint-Eustatius-and-Saba", "Bolivia", "Bhutan", "Bermuda", "Benin", "Belize", "Belgium", "Belarus", "Barbados", "Bangladesh", "Bahrain", "Bahamas", "Azerbaijan", "Austria", "Australia", "Aruba", "Armenia", "Argentina", "Antigua-and-Barbuda", "Antarctica", "Anguilla", "Angola", "Andorra", "American-Samoa", "Algeria", "Albania", "Afghanistan"}

def create_csv(df):
    with open(OUTPUT_FILES['output'], 'w', encoding='utf-8', newline='') as f:
        # File header for Anki
        f.write(f'#separator:Comma\n#html:true\n#notetype:Birds\n#deck:Ultimate Birds\n#tags column:{list(df.columns).index("Tags") + 1}\n#columns:{",".join(df.columns)}\n')
        
        df.to_csv(f, index=False, header=False)

def update_notes(df, notes_file):
    notes = pd.read_csv(notes_file, sep='\t', skiprows=6, header=None, dtype=str, encoding='UTF-8')
    
    # Correct column indices for the notes file
    unique_id_col = 0  # First column is the unique ID
    english_col = 3    # English name column
    scientific_col = 4 # Scientific name column
    ebird_url_col = 10  # eBird URL column
    
    # Create dictionaries to map values to unique IDs (first occurrence)
    ebird_url_to_id = {}
    english_to_id = {}
    scientific_to_id = {}
    
    for _, row in notes.iterrows():
        uid = row[unique_id_col]
        ebird_url = row[ebird_url_col] if pd.notna(row[ebird_url_col]) else None
        english = row[english_col] if pd.notna(row[english_col]) else None
        scientific = row[scientific_col] if pd.notna(row[scientific_col]) else None
        
        # Populate eBird URL dictionary
        if ebird_url and ebird_url not in ebird_url_to_id:
            ebird_url_to_id[ebird_url] = uid
        # Populate English dictionary
        if english and english not in english_to_id:
            english_to_id[english] = uid
        # Populate Scientific dictionary
        if scientific and scientific not in scientific_to_id:
            scientific_to_id[scientific] = uid
    
    # Prepare to collect unique IDs for the new df
    unique_ids = []
    rows_to_keep = []
    
    # Iterate over each row in df to check for matches
    for idx, row in df.iterrows():
        current_ebird = row.get('eBird URL', '')
        current_english = row.get('English', '')
        current_scientific = row.get('Scientific', '')
        matched_id = None
        
        # Check eBird URL first
        if current_ebird in ebird_url_to_id:
            matched_id = ebird_url_to_id[current_ebird]
        else:
            # Check English name
            if current_english in english_to_id:
                matched_id = english_to_id[current_english]
            else:
                # Check Scientific name
                if current_scientific in scientific_to_id:
                    matched_id = scientific_to_id[current_scientific]
        
        if matched_id:
            unique_ids.append(matched_id)
            rows_to_keep.append(idx)
    
    # Filter the df to keep only matched rows and add the unique ID column
    df = df.loc[rows_to_keep].copy()
    df.insert(0, 'Unique ID', unique_ids)

    # Remove splits (they will be added as newly created notes from different file)
    df = df[~df['Unique ID'].duplicated(keep=False)]


    with open(OUTPUT_FILES['output_notes'], 'w', encoding='utf-8', newline='') as f:
        # File header for Anki
        f.write(f'#separator:Comma\n#guid column:1\n#html:true\n#notetype:Birds\n#deck:Ultimate Birds\n#tags column:{list(df.columns).index("Tags") + 1}\n#columns:{",".join(df.columns)}\n')
        
        # Add quotes to avoid skipping if the GUID begins with "#"
        df.to_csv(f, index=False, header=False, quoting=csv.QUOTE_STRINGS)


def combine_data(df, version_tag):
    """
    Combine all processed data into a single DataFrame.
    """
    print("-------- Combining data --------")
    
    # Merge all processed files
    for file in PROCESSED_FILES.values():
        df = pd.merge(df, pd.read_csv(file, na_values=['']), on='Scientific (Clements)', how="left")
    
    df = df.rename(columns={
        'English (Clements)': 'English',
        'Scientific (Clements)': 'Scientific',
        'EBIRD': 'eBird URL',
        'TAXON_ORDER': 'Taxonomic order',
        'ORDER': 'Order',
        'FAMILY': 'Family',
        'TAGS': 'Tags',
        'AVIBASE': 'Avibase URL',
        'CONS_STATUS': 'Conservation status',
        'MNEMONIC': 'Mnemonics',
        'IMAGES': 'Images',
        'DESC': 'Identification',
        'SOUNDS': 'Sounds',
        'Chinese (Traditional)': 'Chinese-traditional'
    })

    # Remove extinct species
    df = df[df['Conservation status'] != 'Extinct']

    # Remove species where BOTH images and sounds are missing
    df = df[~(df['Images'].isna() & df['Sounds'].isna())]

    # Add version tag
    df['Tags'] = df['Tags'] + f' UB::{version_tag}'

    # Save the data as CSV with and without file header
    df.to_csv(OUTPUT_FILES['output_header'], index=False)
    create_csv(df)

    # Update notes from the previous version of the deck and save with unique note ids
    update_notes(df, INPUT_FILES['notes'])