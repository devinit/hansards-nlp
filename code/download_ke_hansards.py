import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from bs4 import BeautifulSoup
from tqdm import tqdm


def main():
    output_dir = os.path.abspath('ke_documents')
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

    base_url = 'https://assembly.nakuru.go.ke/web/business/hansard/'
    base_response = session.get(base_url)
    soup_base = BeautifulSoup(base_response.content, 'html.parser')

    download_cards = soup_base.find_all('div', 'link-template-default')
    for download_card in tqdm(download_cards):
        download_title = download_card.select('h3.package-title')[0].text
        filename = '{}.pdf'.format(download_title)
        download_anchor = download_card.select('a.wpdm-download-link')[0]
        download_url = download_anchor.get('data-downloadurl')
        file_destination = os.path.join(output_dir, filename)
        if not os.path.exists(file_destination):
            file_response = session.get(download_url, allow_redirects=True)
            with open(file_destination, 'wb') as open_destination_file:
                open_destination_file.write(file_response.content)

if __name__ == '__main__':
    main()