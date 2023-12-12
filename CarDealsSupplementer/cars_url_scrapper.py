import re
import requests
from urllib.parse import urlsplit, urlparse
from collections import deque
from bs4 import BeautifulSoup
import pandas as pd

# read url from input
original_url = "https://www.auto-data.net/bg/allbrands"

# to save urls to be scraped
unscraped = deque([original_url])

# to save scraped urls
scraped = set()

# set the base URL
base_url = "https://www.auto-data.net"

# terms to skip
skip_terms = ['login', 'register', 'search', '#']

skip_write = ['brand', 'model', 'generation']

must_contain = ['bg']

# set the maximum depth
# max_depth = 1  # Adjust this value according to your needs

firstUrl = True

output_file = open("scraped_urls.txt", "w")

while len(unscraped):
    # move unscraped_url to scraped_urls set
    url = unscraped.popleft()  # popleft(): Remove and return an element from the left side of the deque

    if not url.startswith(base_url):
        continue  # Skip URLs not starting with the base URL

    # Skip URLs containing specific terms
    if any(term in url for term in skip_terms) and not firstUrl:
        continue

    firstUrl = False

    if not any(keyword in url for keyword in must_contain):
        continue

    scraped.add(url)
    parts = urlsplit(url)

    if parts.query:
        continue

    if '/' in parts.path:
        path = url[:url.rfind('/') + 1]
    else:
        path = url

    try:
        response = requests.get(url)
    except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
        # ignore pages with errors and continue with the next URL
        continue

    # create a beautiful soup for the HTML document
    soup = BeautifulSoup(response.text, 'lxml')

    for anchor in soup.find_all("a"):
        # extract linked URL from the anchor
        if "href" in anchor.attrs:
            link = anchor.attrs["href"]
        else:
            link = ''

        # resolve relative links (starting with /)
        if link.startswith('/'):
            link = base_url + link
        elif not link.startswith('http'):
            link = path + link

        if not link.endswith(".gz") and link.startswith(base_url):
            # Skip URLs containing specific terms
            if any(term in link for term in skip_terms):
                continue

            if urlparse(link).query:
                continue  # Skip URLs with a query string

            if not any(keyword in link for keyword in must_contain):
                continue

            if not link in unscraped and not link in scraped:
                unscraped.append(link)
                print(link)
                if not any(keyword in link for keyword in skip_write):
                    output_file.write(link + "\n")

output_file.close()