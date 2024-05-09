import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm


def initialize_remote_browser():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option("prefs", {
        "download.default_directory": "/tmp/",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False
    })
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


def download_handards_from_page(driver, session, base_url, page_number, output_dir):
    page_url = '{}?page={}'.format(base_url, page_number)
    driver.get(page_url)

    folder_titles = driver.find_elements(By.XPATH, "//h3[@class='field-content']")
    folder_title_texts = [folder_title.text for folder_title in folder_titles]
    folder_title_urls = [folder_title.find_element(By.XPATH, ".//a").get_attribute('href') for folder_title in folder_titles]
    for i in range(0, len(folder_title_texts)):
        folder_title_text = folder_title_texts[i]
        output_folder_dir = os.path.join(output_dir, folder_title_text)
        if not os.path.exists(output_folder_dir):
            os.mkdir(output_folder_dir)

        folder_url = folder_title_urls[i]
        
        driver.get(folder_url)
        link_divs = driver.find_elements(By.XPATH, "//div[@class='cmisviews']")
        link_div_texts = [link_div.text for link_div in link_divs]
        link_div_urls = [link_div.find_element(By.XPATH, ".//a").get_attribute('href') for link_div in link_divs]
        for j in range(0, len(link_div_texts)):
            filename = link_div_texts[j]
            link_div_url = link_div_urls[j]
            file_destination = os.path.join(output_folder_dir, filename)
            if not os.path.exists(file_destination):
                file_response = requests.get(link_div_url, allow_redirects=True)
                with open(file_destination, 'wb') as open_destination_file:
                    open_destination_file.write(file_response.content)

def main():
    output_dir = os.path.abspath('documents')
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

    base_url = 'https://www.parliament.go.ug/documents/hansards'
    base_response = session.get(base_url)
    soup_base = BeautifulSoup(base_response.content, 'html.parser')

    last_page_url = soup_base.find('a', title='Go to last page').get('href')
    parsed_last_page_url = urlparse(last_page_url)
    last_page = int(parse_qs(parsed_last_page_url.query)['page'][0])

    driver = initialize_remote_browser()
    
    for page_number in tqdm(range(0, last_page + 1)):
        download_handards_from_page(driver, session, base_url, page_number, output_dir)

    driver.close()

if __name__ == '__main__':
    main()