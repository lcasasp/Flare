import json
import concurrent.futures
from newsplease import NewsPlease
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import Urls, db
from app import app
import requests
from datetime import datetime
import time

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

session = requests.Session()

#Efficiency: 319 articles / 482   
#Time: 531.5 seconds
def scrape_url(url):
    try:
        response = session.head(url.url)
        content_type = response.headers.get('Content-Type', '')

        if 'text/html' not in content_type:
            print(f"Skipping non-HTML URL: {url.url}")
            return None

        article = NewsPlease.from_url(url.url)
        if article:
            return article.get_dict()
        else:
            print(f"NewsPlease could not extract data from URL: {url.url}")
            return None
    except Exception as e:
        print(f"Could not scrape URL {url.url}: {e}")
        return None

def scrape_all_urls_and_write_json():
    start = time.time()

    with app.app_context():
        urls = Urls.query.all()
        results = {'Results': []}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_url = {executor.submit(scrape_url, url): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                    if data is not None:
                        results['Results'].append(data)
                except Exception as exc:
                    print(f"Generated an exception: {exc} with url {url.url}")

    end = time.time()
    time_elapsed = end - start
    print("Time elapsed: " + str(time_elapsed))

    with open('results.json', 'w') as f:
         json.dump(results, f, cls=DateTimeEncoder, indent=4)


if __name__ == "__main__":
    scrape_all_urls_and_write_json()