import json
import concurrent.futures
from newspaper import Article
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Urls, db
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

def scrape_url(url):
    try:
        response = session.head(url.url)
        if response.status_code == 200: 
            article = Article(url.url)
            article.download()
            article.parse()

            if article.text: 
                article_data = {
                    "authors": article.authors,
                    "title": article.title,
                    "publish_date": article.publish_date.isoformat() if article.publish_date else None,
                    "text": article.text,
                    "url": url.url
                }
                return article_data
    except Exception as e:
        print(f"Could not scrape URL {url.url}: {e}")
    return None

def read_existing_results(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {'Results': []}

def scrape_all_urls_and_write_json():
    start = time.time()

    existing_results = read_existing_results('results.json')

    with app.app_context():
        urls = Urls.query.all()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_url = {executor.submit(scrape_url, url): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                    if data and data['text']:
                        existing_results['Results'].append(data)
                except Exception as exc:
                    print(f"Generated an exception: {exc} with url {url.url}")

    end = time.time()
    print("Time elapsed: " + str(end - start))

    with open('results.json', 'w') as f:
         json.dump(existing_results, f, cls=DateTimeEncoder, indent=4)

if __name__ == "__main__":
    scrape_all_urls_and_write_json()