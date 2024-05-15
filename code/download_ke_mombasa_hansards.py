import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from bs4 import BeautifulSoup
from tqdm import tqdm


def main():
    output_dir = os.path.abspath('mombasa_documents')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    # Define the retry strategy
    retry_strategy = Retry(
        total=10,  # Maximum number of retries
        backoff_factor=2,  # Exponential backoff factor (e.g., 2 means 1, 2, 4, 8 seconds, ...)
        status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry on
    )
    # Create an HTTP adapter with the retry strategy and mount it to session
    adapter = HTTPAdapter(max_retries=retry_strategy)

    # Create a new session object
    session = requests.Session()
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    base_url = 'https://www.mombasaassembly.go.ke/courses-type/hansard/'
    base_response = session.get(base_url)
    soup_base = BeautifulSoup(base_response.content, 'html.parser')

    nav_links = soup_base.find_all('a', 'page-numbers')
    last_page_number = int(nav_links[1].text)
    
    for page in tqdm(range(1, last_page_number + 1)):
        page_url = '{}/page/{}/'.format(base_url, page)
        page_response = session.get(page_url)
        soup_page = BeautifulSoup(page_response.content, 'html.parser')

        download_cards = soup_page.find_all('h4', 'entry-title')
        for download_card in tqdm(download_cards):
            try:
                download_anchor = download_card.select('a')[1]
            except IndexError:
                next
            download_url = download_anchor.get('href')
            filename = os.path.basename(download_url)
            file_destination = os.path.join(output_dir, filename)
            if not os.path.exists(file_destination):
                file_response = session.get(download_url, allow_redirects=True)
                with open(file_destination, 'wb') as open_destination_file:
                    open_destination_file.write(file_response.content)

if __name__ == '__main__':
    main()