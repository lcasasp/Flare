import json
import requests
import os
from newsapi import NewsApiClient
from flask import Flask, current_app, request, render_template
from dotenv import load_dotenv
from bs4 import BeautifulSoup
# Load environment variables from .env file
load_dotenv()
from elasticsearch import Elasticsearch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import News, Urls, db

API_KEY = os.environ.get("API_KEY", None)

#Note, these News API keys are subject to change, used only for testing
keys = "Energy 'climate'"
newsapi = NewsApiClient(api_key=API_KEY)

app = Flask(__name__)
db_filename = "news.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False

db.init_app(app)
with app.app_context():
    db.create_all()

ELASTIC_PW = os.environ.get("ELASTIC_PW", None)
# Connect to Elasticsearch
es = Elasticsearch(
    ["https://localhost:9200"],
    basic_auth=('elastic', ELASTIC_PW),
    verify_certs=False,
)

@app.route('/')
def index():
    return render_template('index.html')

def success_response(data, code=200):
    return json.dumps(data), code

def failure_response(message, code=404):
    return json.dumps({"error": message}), code

"""Endpoint: /add
    This route is responsible for updating the database with the latest news articles based on the search query.
    It fetches JSON data from the News API using the get_everything() method provided by the newsapi object.
    Then it loops through the articles and adds or updates them in the database using the News model.
    After updating the database, it calls the index_articles() function to index the newly added data into Elasticsearch.
    It returns a success response message if all data has been added.
Status Code: 200 OK
"""
@app.route('/add')
def addData():
    #TODO Get data in results.json and populate News db
    with open('results.json') as f:
        data = json.load(f)


"""
Helper function for the "/" index route
This function indexes the data from the database into
an elasticsearch index using the mapping provided.
"""
def index_articles():
    # Create an Elasticsearch index
    index_name = "articles"
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)

    # Define the mapping for your data to be indexed
    mapping = {
        "properties": {
            "source": {
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "keyword"}
                }
            },
            "author": {"type": "keyword"},
            "title": {"type": "keyword"},
            "description": {"type": "text"},
            #Note, URL not referenced for indexing, and should be returned
            # AFTER search query as result, not useful for query.
            "date": {"type": "date_nanos"},
            "content": {"type": "text"}
        }
    }
    es.indices.put_mapping(body=mapping, index=index_name)

    for article in News.query.all():
        # Create a document to index
        doc = {
            "source": {
                "id": article.source_id,
                "name": article.source_name,
            },
            "author": article.author,
            "title": article.title,
            "description": article.description,
            "date": article.published_at,
            "content": article.content
        }
        # Index the document in Elasticsearch
        try:
            es.index(index=index_name, body=doc)
        except Exception as e:
            current_app.logger.error(f"Error indexing document {article.id}: {e}")
    es.indices.refresh(index=index_name)

@app.route("/addurls")
def addurls():
    scrape_google_scholar_metadata()
    addNewsUrl()
    return success_response({"urls": [c.serialize() for c in Urls.query.all()]})

"""
Helper function for /addurls, scrapes google scholar to add more data that is tailored
to expert level viewers. Uses beautifulsoup and stores all urls from search into Urls db 
"""
def scrape_google_scholar_metadata():
    base_url = "https://scholar.google.com"
    metadata = []

    for page in range(5):
        query_url = f"{base_url}/scholar?q=energy 'climate change'&start={page*10}&scisbd=1"
        response = requests.get(query_url)
        soup = BeautifulSoup(response.content, "html.parser")

        results = soup.find_all("div", class_="gs_r")

        for result in results:
            # Extract URL
            url_element = result.find("div", class_="gs_ggsd")
            url = url_element.find("a")["href"] if url_element else ""

            # Create metadata dictionary
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
    return success_response({"Urls": [c.serialize() for c in Urls.query.all()]})

def addNewsUrl():
    data = newsapi.get_everything(q=keys,
                                language='en',
                                sort_by='popularity')

    # Loop through articles and add/update them in the database
    for article_data in data['articles']:
        # check if an article with the same URL already exists
        if db.session.query(News).filter_by(url=article_data['url']).first():
            print(f"Article with URL {article_data['url']} already exists in database.")
            continue

        # Create new article if it doesn't exist in the database
        url = Urls(     
            url=article_data['url'],
        )
        db.session.add(article)
    db.session.commit()

    
@app.route("/news")
def get_news():
    return success_response({"news": [c.serialize() for c in News.query.all()]})
@app.route("/urls")
def get_urls():
    return success_response({"urls": [c.serialize() for c in Urls.query.all()]})

@app.route('/query', methods=['POST'])
def query():
    search_query = request.form['search_query']
    # Note, to change the query parameters, change the query dictionary.
    query = {
        "match": {
            "content": search_query,
        }
    }
    # Execute the search query
    es_result = es.search(index="articles", query=query)
    article_ids = [hit['_source']['title'] for hit in es_result['hits']['hits']]
    # Fetch the articles from the database
    articles = News.query.filter(News.title.in_(article_ids)).all()
    results = {"news": [article.serialize() for article in articles]}
    return render_template('results.html', results=results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)