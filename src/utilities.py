import os
import json
import constants
import requests
from bs4 import BeautifulSoup
from models import db, News, Urls
from newsapi import NewsApiClient
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()
ELASTIC_PW = os.environ.get("ELASTIC_PW", None)
# Connect to Elasticsearch
es = Elasticsearch(
    ["https://localhost:9200"],
    basic_auth=('elastic', ELASTIC_PW),
    verify_certs=False,
)

API_KEY = os.environ.get("API_KEY", None)

#Note, these News API keys are subject to change, used only for testing
keys = "Energy 'climate'"
newsapi = NewsApiClient(api_key=API_KEY)

def index_articles(es):
    # Create an Elasticsearch index
    index_name = "articles"
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)

    # Define the mapping for your data to be indexed
    mapping = {
        "settings": {
            "analysis": {
                "analyzer": {
                    "english_content_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "english_stop",
                            "english_stemmer"
                        ]
                    }
                },
                "filter": {
                    "english_stop": {
                        "type": "stop",
                        "stopwords": "_english_"
                    },
                    "english_stemmer": {
                        "type": "stemmer",
                        "language": "english"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "source_domain": {"type": "keyword"},
                "authors": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "english_content_analyzer"},
                "description": {"type": "text", "analyzer": "english_content_analyzer"},
                "date": {"type": "date_nanos"},
                "content": {"type": "text", "analyzer": "english_content_analyzer"}
            }
        }
    }

    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body=mapping)

    for article in News.query.all():
        # Create a document to index
        doc = {
            "source": article.source_domain,
            "authors": article.authors,
            "title": article.title,
            "date": article.date,
            "content": article.content
        }
        # Index the document in Elasticsearch
        try:
            es.index(index=index_name, body=doc)
        except Exception as e:
            current_app.logger.error(f"Error indexing document {article.id}: {e}")
    es.indices.refresh(index=index_name)


def scrape_google_scholar_metadata(self):
    base_url = "https://scholar.google.com"
    metadata = []

    for page in range(constants.GOOGLE_SCHOLAR_PAGE_DEPTH):
        query_url = f"{base_url}/scholar?q=energy 'climate change'&start={page*10}&scisbd=1"
        response = requests.get(query_url)
        soup = BeautifulSoup(response.content, "html.parser")

        results = soup.find_all("div", class_="gs_r")

        for result in results:
            # Extract URL
            url_element = result.find("div", class_="gs_ggsd")
            url = url_element.find("a")["href"] if url_element else ""

            # Create metadata dictionary
            if (url != ""):
                metadata.append({
                    "url": url,
                })

    for url in metadata:
        # check if an article with the same URL already exists
        if db.session.query(Urls).filter_by(url=url['url']).first():
            print(f"Article with URL {url['url']} already exists in database.")
            continue

        # Create new article if it doesn't exist in the database
        url = Urls(
            url=url['url'],
        )
        db.session.add(url)
    db.session.commit()

def addNewsUrl(self):
    data = newsapi.get_everything(q=keys,
                            language='en',
                            sort_by='popularity')

    # Loop through articles and add/update them in the database
    pages = data['totalResults'] // 100 + 1
    if pages > constants.NEWS_API_PAGE_DEPTH:
        pages = constants.NEWS_API_PAGE_DEPTH
    for page in range(1, pages):
        data = newsapi.get_everything(q=keys,
                                language='en',
                                sort_by='popularity',
                                page=page)
        for article_data in data['articles']:
            # Check if an URL with the same URL already exists in the Urls table
            if db.session.query(Urls).filter_by(url=article_data['url']).first():
                print(f"URL {article_data['url']} already exists in database.")
                continue

            # Create new Url object if it doesn't exist in the database
            url = Urls(url=article_data['url'])
            db.session.add(url)
        db.session.commit()


def success_response(data, code=200):
    return json.dumps(data), code

def failure_response(message, code=404):
    return json.dumps({"error": message}), code