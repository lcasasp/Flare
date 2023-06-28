import json
from newsplease import NewsPlease
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import Urls, db
from app import app
import requests
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return super().default(o)

#NOTE, SCRAPING EFFICIENCY:
    507/946 articles scraped succesfully
def scrape_all_urls_and_write_json():
    #delete current results.json file
    with open('results.json', 'w') as f:
        f.write("")

    with app.app_context():
        urls = Urls.query.all()
        results = {'Results': []}

        for url in urls:
            try:
                response = requests.head(url.url)
                content_type = response.headers.get('Content-Type', '')

                if 'text/html' not in content_type:
                    print(f"Skipping non-HTML URL: {url.url}")
                    continue

                article = NewsPlease.from_url(url.url)
                if article:
                    results['Results'].append(article.get_dict())
                else:
                    print(f"NewsPlease could not extract data from URL: {url.url}")
            except Exception as e:
                print(f"Could not scrape URL {url.url}: {e}")

        with open('results.json', 'w') as f:
             json.dump(results, f, cls=DateTimeEncoder, indent=4)

if __name__ == "__main__":
    scrape_all_urls_and_write_json()