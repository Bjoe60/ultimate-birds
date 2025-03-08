import pandas as pd
from file_paths import INPUT_FILES, PROCESSED_FILES

def create_anki_audio(aud_type, credit, file, spectrogram):
    aud_type = '' if pd.isna(aud_type) else aud_type.replace('?', '')
    return f'<div class="aud-w-txt"><div class="aud-type">{aud_type}</div><div class="aud-credit">© {credit}</div><audio controls="" controlslist="nodownload noplaybackrate"><source src="{file}" type="audio/mpeg"></audio><img src="{spectrogram}"></div>'

def get_audio(base_df):
    print('-------- Scraping audio --------')
    df = base_df[['Scientific (Clements)', 'English (Clements)', 'Scientific (IOC)', 'English (IOC)']].copy()
    df['SOUNDS'] = pd.NA

    # Load and merge audio datasets
    media_df = pd.read_csv(INPUT_FILES['audio_files'], usecols=['associatedObservationReference', 'format', 'accessURI', 'description', 'caption', 'rightsHolder', 'Rating'], encoding='UTF-8', dtype={'Rating': 'Int64'})
    occurrence_df = pd.read_csv(INPUT_FILES['audio_data'], usecols=['occurrenceID', 'behavior', 'Associated Taxa', 'eventDate', 'vernacularName', 'scientificName'])

    # Merge audio data on occurrence ID
    merged_audio = pd.merge(media_df, occurrence_df, left_on='associatedObservationReference', right_on='occurrenceID', how='inner')
    print(f'Found {len(merged_audio)} audio files')

    # Replace subspecies with species name
    merged_audio['scientificName'] = merged_audio['scientificName'].str.split(' ').str[:2].str.join(' ')

    # Precompute dictionaries for fast lookup.
    # Group by scientificName and vernacularName so that for each species we avoid filtering the whole DataFrame.
    sci_dict = {name: group for name, group in merged_audio.groupby('scientificName')}
    vern_dict = {name: group for name, group in merged_audio.groupby('vernacularName')}

    def process_species_audio(species_row):
        sci_name = species_row['Scientific (Clements)']
        com_name = species_row['English (Clements)']
        sci_name_ioc = species_row['Scientific (IOC)']
        com_name_ioc = species_row['English (IOC)']
        matches = None
        if sci_name in sci_dict:
            matches = sci_dict[sci_name]
        elif com_name in vern_dict:
            matches = vern_dict[com_name]
        elif sci_name_ioc in sci_dict:
            matches = sci_dict[sci_name_ioc]
        elif com_name_ioc in vern_dict:
            matches = vern_dict[com_name_ioc]
        if matches is not None:
            audio_files = matches[matches['format'] == 'audio/mp3']

            # Filter for spectrogram rows: those with a caption starting with "Spectrogram"
            matches['caption'] = matches['caption'].fillna('')
            spectrogram_rows = matches[matches['caption'].str.startswith("Spectrogram")]

            # Build a mapping from associatedObservationReference to spectrogram URL (here assumed to be in 'accessURI')
            spec_map = spectrogram_rows.set_index('associatedObservationReference')['accessURI']

            # For each row in audio_files, map its associatedObservationReference to the spectrogram URL
            audio_files['spectrogram'] = audio_files['associatedObservationReference'].map(spec_map)
            
            # Avoid similar recordings made by the same person on the same day.
            audio_files = audio_files.drop_duplicates(subset=['rightsHolder', 'eventDate'])

            # Prioritise audio files with a maximum length of 30 seconds.
            audio_files = audio_files.dropna(subset=['description'])
            audio_files['duration'] = audio_files['description'].str.extract(r'(\d+) s').astype(int)
            if not audio_files[audio_files['duration'] <= 30].empty:
                # If there is at least one recording <= 30 seconds, use only those.
                audio_files = audio_files[audio_files['duration'] <= 30]
            elif not audio_files[audio_files['duration'] <= 60].empty:
                # Otherwise, if there is at least one recording <= 60 seconds, use those.
                audio_files = audio_files[audio_files['duration'] <= 60]
            # Else, leave audio_files as is (i.e. use recordings of any length).

            audio_files['Rating'] = audio_files['Rating'].fillna(1)

            # Priority is given to recording with no additional species in the backgorund and a rating of 3 or higher.
            audio_files['background_priority'] = audio_files.apply(
                lambda row: 1 if pd.isna(row['Associated Taxa']) and row['Rating'] >= 3
                            else 0,
                axis=1
            )

            # Sort by priorities and rating.
            audio_files = audio_files.sort_values(['background_priority', 'Rating', 'duration'], ascending=[False, False, True])

            unique_audio = audio_files.head(10)
            # Create the HTML snippet from each audio match.
            audio_html = ''.join(
                create_anki_audio(
                    audio_row['behavior'],
                    audio_row['rightsHolder'],
                    audio_row['accessURI'],
                    audio_row['spectrogram']
                )
                for _, audio_row in unique_audio.iterrows()
            )
            return audio_html
        else:
            return ''

    # Apply the per-species processing (this is still row-by-row but each lookup is fast).
    df['SOUNDS'] = df.apply(process_species_audio, axis=1)

    df['SOUNDS'] = df['SOUNDS'].replace('', pd.NA)
    print(f'Found audio for {df["SOUNDS"].count()} species')

    # Save the final DataFrame.
    df[['Scientific (Clements)', 'SOUNDS']].to_csv(PROCESSED_FILES['audio'], index=False)