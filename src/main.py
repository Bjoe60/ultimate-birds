from base_data import get_base_data
from translations import merge_translations
from mnemonics import process_mnemonics
from avibase import scrape_avibase_data
from images import scrape_images
from audio import get_audio
from combine_data import combine_data

def main():
    df = get_base_data()

    # Optionally run independent processes in any order
    # merge_translations(df)
    # process_mnemonics(df)
    # scrape_avibase_data(df)
    # scrape_images(df)
    # get_audio(df)
    
    # Combine results
    combine_data(df, 'version-2025-03-08')


if __name__ == "__main__":
    main()