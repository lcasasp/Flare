import os
from flask import Flask
from flask_cors import CORS, cross_origin
from elasticsearch import Elasticsearch
from newsapi import NewsApiClient
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from FlaskAppHandler import FlaskAppHandler
from models import db, News, Urls
import constants

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configure your app for the SQLALCHEMY_DATABASE_URI
db_filename = "news.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False

# Initialise Elasticsearch and NewsAPI
load_dotenv()
ELASTIC_PW = os.environ.get("ELASTIC_PW", None)
# Connect to Elasticsearch
es = Elasticsearch(
    ["https://localhost:9200"],
    basic_auth=('elastic', ELASTIC_PW),
    verify_certs=False,
)

# Create a FlaskAppHandler instance
flask_app_handler = FlaskAppHandler(app, db)

# Register routes and run the app
if __name__ == "__main__":
    flask_app_handler.run()