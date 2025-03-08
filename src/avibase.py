from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import numpy as np
from file_paths import PROCESSED_FILES
from utils import fetch_url
from tqdm import tqdm

BASE_URL_AVIBASE = "https://avibase.bsc-eoc.org/"
DIVERSE_COUNTRIES = {
    'Australia': 275, 'Brazil': 67, 'Canada': 6, 'China': 239, 'Colombia': 58,
    'Ecuador': 64, 'India': 244, 'Indonesia': 268, 'Peru': 65, 
    'Russian Federation': 230, 'United States': 8
}
XPATH = '/html/body/div[1]/div[4]/div/div[5]/table/tr[{}]/td[1]/a[2]'

def initialize_webdriver():
    """Initialize and return a Selenium WebDriver instance."""
    service = Service()
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def fetch_country_regions(driver, country_name):
    """Fetch <a> tags for regions in a given country."""
    country_code = DIVERSE_COUNTRIES.get(country_name)
    if not country_code:
        return []

    try:
        driver.get(BASE_URL_AVIBASE + 'checklist.jsp?lang=EN')
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'reg3')))
        
        # Select country
        driver.find_element(By.XPATH, XPATH.format(country_code)).click()
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'reg6')))

        # Parse regions
        soup = BeautifulSoup(driver.page_source, 'lxml')
        tr_class = 'reg4' if country_name == 'Russian Federation' else ['reg4', 'reg5', 'reg6']
        return [tr.td.a for tr in soup.find_all('tr', class_=tr_class)]
        
    except Exception as e:
        print(f"Error fetching regions for {country_name}: {str(e)}")
        return []

def scrape_region_data(df, region_url, country_name, region_name):
    """Scrape data for a single region and update DataFrame."""
    try:
        response = fetch_url(region_url)
        if not response:
            return

        soup = BeautifulSoup(response.content, 'lxml')
        
        # Use passed region_name instead of parsing from URL
        region_name = region_name.strip()
        
        for bird_row in soup.find_all('tr', class_='highlight1'):
            name = bird_row.td.text
            rarity = next((text.rstrip() for text in bird_row.td.next_sibling.next_sibling.contents 
                          if isinstance(text, str) and text.strip()), 'Common')
            
            if (breeding := bird_row.find('font', color='blue')):
                rarity = breeding.text

            tag = f'UB::{country_name}::{region_name}::{rarity}'
            tag = tag.replace(' ', '-') + ' '

            if rarity == 'Extirpated':
                tag = ''
            
            mask = df['English (Clements)'] == name
            df.loc[mask, 'TAGS'] = df.loc[mask, 'TAGS'] + tag

    except RequestException as e:
        print(f"Request error for {region_url}: {str(e)}")


def scrape_country(df, soup, country):
    """Scrape bird data for a country and update the DataFrame."""
    bird_rows = soup.find_all('tr', class_='highlight1')

    for bird_row in bird_rows:
        name = bird_row.td.text
        avibase_url = BASE_URL_AVIBASE + bird_row.td.next_sibling.a['href']
        rarity_cons_stat = bird_row.td.next_sibling.next_sibling.contents

        rarity = ''
        for text in rarity_cons_stat:
            if isinstance(text, str) and not text == ' ':
                rarity = text.rstrip()

        breeding_endemic = bird_row.find('font', color='blue')
        if breeding_endemic:
            rarity = breeding_endemic.text

        tag = f'UB::{country}::{(rarity if rarity else "Common")}'
        tag = tag.replace(' ', '-') + ' '

        if rarity == 'Extirpated':
            tag = ''

        conservation_status = bird_row.find('font', color='red')
        conservation_status = conservation_status.text if conservation_status else "Least concern"

        # Update DataFrame with scraped tags
        row = df['English (Clements)'] == name
        df.loc[row, 'TAGS'] = df.loc[row, 'TAGS'] + tag
        if df.loc[row, 'AVIBASE'].array and pd.isnull(df.loc[row, 'AVIBASE'].array[0]):
            df.loc[row, 'AVIBASE'] = avibase_url
            df.loc[row, 'CONS_STATUS'] = conservation_status


def process_country(df, a_tag):
    """Process a country and its regions."""
    try:
        # Scrape country data
        country_url = BASE_URL_AVIBASE + a_tag['href']
        country_name = a_tag.text

        # Country-level scraping
        response = fetch_url(country_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            scrape_country(df, soup, country_name)
        
        # Modified region processing section
        if country_name in DIVERSE_COUNTRIES:
            region_driver = initialize_webdriver()
            region_links = fetch_country_regions(region_driver, country_name)
            region_driver.quit()

            # Loop through each region link sequentially
            for link in region_links:
                scrape_region_data(
                    df, 
                    BASE_URL_AVIBASE + link['href'],  # Construct full URL
                    country_name,
                    link.text  # Pass region name from <a> tag text
                )

    except Exception as e:
        print(f"Error processing {country_name}: {str(e)}")


def scrape_avibase_data(df_base):
    """
    Main function to get avibase urls, conservation status and country rarities.
    Avibase uses Clements taxonomy.
    """
    print('-------- Starting Avibase scraping --------')
    df = df_base[['Scientific (Clements)', 'English (Clements)']].copy()
    df['TAGS'] = ''
    for col in ['AVIBASE', 'CONS_STATUS']:
        df[col] = pd.NA
    
    # Initialize main driver for country list
    main_driver = initialize_webdriver()
    main_driver.get(BASE_URL_AVIBASE + 'checklist.jsp?lang=EN')
    
    try:
        WebDriverWait(main_driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'reg3'))
        )
        country_links = BeautifulSoup(main_driver.page_source, 'lxml').find_all('tr', class_='reg3')
    finally:
        main_driver.quit()

    for link in tqdm(country_links, desc="Processing countries"):
        process_country(df, link.td.a)
    
    # Save final data
    df = df.drop(columns=['English (Clements)'])
    df.to_csv(PROCESSED_FILES['avibase'], index=False)