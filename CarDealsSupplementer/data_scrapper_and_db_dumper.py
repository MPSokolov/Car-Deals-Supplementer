import re
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

file_path = 'scraped_urls.txt'
with open(file_path, 'r') as file:
    urls = file.read().splitlines()

# urls = ["https://www.auto-data.net/bg/chevrolet-camaro-v-6.2-v8-400hp-hydra-matic-24906",
#         "https://www.auto-data.net/bg/daihatsu-sonica-0.66l-r3-12v-turbo-64hp-100",
#         "https://www.auto-data.net/bg/hyundai-galloper-ii-3.0-i-v6-161hp-13714"]

client = MongoClient('mongodb://localhost:27017/')

db = client['scraper_test_db']

# Create or connect to a collection within the database
collection = db['cars']

for url in urls:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    table_rows = soup.find_all('tr')

    # Initialize an empty dictionary to store the data
    car_info = {}

    # Loop through each table row
    for row in table_rows:
        # Extract the table headers (th) and data cells (td)
        headers = row.find_all('th')
        data_cells = row.find_all('td')

        # If there are both headers and data cells, store the information in the dictionary
        if headers and data_cells:
            header_text = headers[0].text.strip()
            data_text = re.sub(r'\s+', ' ', data_cells[0].text.strip())

            if "Влезте, за да видите." not in data_text:
                # Add the key-value pair to the dictionary
                car_info[header_text] = data_text

    collection.insert_one(car_info)

client.close()
