INPUT_FOLDER = "data/input/"
INPUT_FILES = {
    "ebird_taxonomy": INPUT_FOLDER + "eBird_taxonomy_v2025.csv",
    "ebird_translations": INPUT_FOLDER + "eBird_Taxonomy_v2024_5-tab_5Sep2025a.xlsx",
    "avilist_taxonomy": INPUT_FOLDER + "AviList-v2025-11Jun-extended.xlsx",
    "mnemonics": INPUT_FOLDER + "Mnemonics.txt",
    "old_version": INPUT_FOLDER + "Ultimate Birds - old version.csv",
    "audio_files": INPUT_FOLDER + "wildlife-sounds-birds.dwca/Multimedia.txt",
    "audio_data": INPUT_FOLDER + "wildlife-sounds-birds.dwca/Occurrence.txt",
    "notes": INPUT_FOLDER + "Ultimate Birds.txt",
    "danish_translations_dofbasen": INPUT_FOLDER + "dofbasen.csv",
    "danish_translations_navnegruppen": INPUT_FOLDER + "IOC-DOF_-_NAVNE_P_ALVERDENS_FUGLE_-_20-12-2024.xlsx",
}

PROCESSED_FOLDER = "data/processed/"
PROCESSED_FILES = {
    "avibase": PROCESSED_FOLDER + "avibase.csv",
    "translations": PROCESSED_FOLDER + "translations.csv",
    "mnemonics": PROCESSED_FOLDER + "mnemonics.csv",
    "images": PROCESSED_FOLDER + "images.csv",
    "audio": PROCESSED_FOLDER + "audio.csv",
}

OUTPUT_FOLDER = "data/output/"
OUTPUT_FILES = {
    "output": OUTPUT_FOLDER + "Ultimate Birds.csv",
    "output_header": OUTPUT_FOLDER + "Ultimate Birds_header.csv",
    "output_notes": OUTPUT_FOLDER + "Ultimate Birds_notes.txt",
    "base_data": OUTPUT_FOLDER + "base_data.csv",
    "clements_vs_avilist": OUTPUT_FOLDER + "clements_vs_avilist.csv",
}