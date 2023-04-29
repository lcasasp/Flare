import json
import requests
import os
from newsapi import NewsApiClient
from flask import Flask, current_app, request
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
from elasticsearch import Elasticsearch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import News, db

API_KEY = os.environ.get("API_KEY", None)

#Note, these News API keys are subject to change, used only for testing
keys = "Energy"
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

"""
Helper function for the "/" index route
This function indexes the data from the database into
an elasticsearch index using the mapping provided.
"""
def index_articles():
    # Create an Elasticsearch index
    index_name = "articles"
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
            #Note, URL and URL_toImage are not referenced for indexing, and should be returned
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

def success_response(data, code=200):
    return json.dumps(data), code

def failure_response(message, code=404):
    return json.dumps({"error": message}), code

"""Endpoint: /
HTTP Method: GET

Access: Public
Functionality:
    This route is responsible for updating the database with the latest news articles based on the search query.
    It fetches JSON data from the News API using the get_everything() method provided by the newsapi object.
    Then it loops through the articles and adds or updates them in the database using the News model.
    After updating the database, it calls the index_articles() function to index the newly added data into Elasticsearch.
    It returns a success response message if all data has been added.
    Request Parameters:
        None
Response:

Status Code: 200 OK
Content: JSON object with the following fields:
    "message": A success message indicating that all data has been added."""
@app.route('/')
def index():
    db.session.query(News).delete()
    db.session.commit()
    # Make API request to get JSON data
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
        article = News(
            status=data['status'],
            total_results=data['totalResults'],
            source_id=article_data['source']['id'],
            source_name=article_data['source']['name'],
            author=article_data['author'],
            title=article_data['title'],
            description=article_data['description'],
            url=article_data['url'],
            url_to_image=article_data['urlToImage'],
            published_at=article_data['publishedAt'],
            content=article_data['content']
        )
        db.session.add(article)
    db.session.commit()

    index_articles()
    return success_response("added all data.")

@app.route("/news")
def get_news():
    return success_response({"news": [c.serialize() for c in News.query.all()]})

"""
Endpoint: /query
HTTP Method: GET

Response:
    Success response (HTTP status code 200): a JSON object containing the matching news articles. The response format should be as follows:
    If there are no matching news articles, the response should be an empty array [].

Error responses:
    None

Functionality:
    Executes a search query for articles containing the term "energy" in the content field of the Elasticsearch index.
    Returns a JSON object containing the matching news articles.
"""
@app.route("/query")
def query():
    # Note, to change the query parameters, change the query dictionary.
    query = {
        "match": {
            "content": "energy",
            "content": "climate"
        }
    }

    # Execute the search query
    results = es.search(index="articles", query=query)
    
    return success_response({"news": [hit['_source']['source']['name'] for hit in results['hits']['hits']]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)