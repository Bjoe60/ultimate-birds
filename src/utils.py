from urllib.parse import quote
import requests
import time

"""
Escape special characters in text
"""
def escape_characters(text):
    return text.replace(';;', quote(';;')).replace('|', quote('|')).replace('\xa0', '&nbsp;')


"""
Get the URL content, but retry a few times if there's an error
"""
MAX_RETRIES = 3
RETRY_DELAY = 2

def fetch_url(url):
    for i in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0', 'From': 'bjorn60@gmail.com'}, timeout=120)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Attempt {i + 1}: Error accessing {url} - {e}")
            if i < MAX_RETRIES - 1:  # Don't wait on the last retry
                time.sleep(RETRY_DELAY)  # Add a delay before retrying
    print(f"Failed to access {url} after {MAX_RETRIES} attempts.")
    return None