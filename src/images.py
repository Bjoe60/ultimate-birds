from bs4 import BeautifulSoup
from file_paths import PROCESSED_FILES
from utils import fetch_url
from tqdm import tqdm

def scrape_images_for_species(df, idx):
    """
    Scrape images for a single species from its EBIRD page and update the DataFrame.
    
    Args:
        df (pd.DataFrame): The DataFrame containing species information.
        idx (int): The index of the species to process.
    """
    url = df.loc[idx, 'EBIRD']
    
    response = fetch_url(url)
    if not response:
        return

    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find the container with the images.
    img_container = soup.find('div', class_='Hero-image')
    if not img_container:
        print(f"No image container found on page: {url}")
        return

    anki_imgs = ""
    
    # Iterate through the child elements of the image container.
    for figure in img_container.find_all('figure'):
        try:
            # Locate the image tag.
            img_tag = figure.find('img')
            if not img_tag:
                continue

            # Adjust image URL for higher resolution.
            img_url = img_tag.get('src')
            if not img_url:
                continue
            img_url = img_url[:-3] + "640"

            # Extract metadata (description and credit) from the figcaption.
            figcaption = figure.find('figcaption')
            if figcaption:
                spans = figcaption.find_all('span')
                if len(spans) > 1:
                    # For images with both description and credit.
                    type = spans[0].text
                    credit = spans[1].text
                else:
                    # For images with only credit.
                    type = ''
                    credit = spans[0].text
            else:
                type = ''
                credit = ''

            # Build an HTML for the image.
            anki_imgs += (
                f'''<div class="img-w-txt">'''
                f'''<div class="type">{type}</div>'''
                f'''<img src="{img_url}">'''
                f'''<div class="credit">{credit.replace('\xa0', '&nbsp;')}</div>'''
                f'''</div>'''
            )
        except Exception as e:
            print(f"Error processing image figure for {url}: {e}")

    # Scrape identification info
    identification = soup.find('p', class_='u-stack-sm')
    identification = identification.text if identification else ""
    soup.decompose()

    # Update the DataFrame safely.
    df.loc[idx, 'IMAGES'] = anki_imgs
    df.loc[idx, 'DESC'] = identification

def scrape_images(base_df):
    """
    Scrape images for all species listed in the input CSV file and write the results to an output CSV.
    """
    print("-------- Scraping Images --------")
    df = base_df[['Scientific (Clements)', 'EBIRD']].copy()

    # Process each species one at a time to avoid overloading the site.
    for idx in tqdm(df.index, desc="Scraping images"):
        scrape_images_for_species(df, idx)

    df.drop(columns=['EBIRD'], inplace=True)
    
    df.to_csv(PROCESSED_FILES['images'], index=False)
