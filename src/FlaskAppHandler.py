import json
from utilities import index_articles, scrape_google_scholar_metadata, addNewsUrl, success_response, failure_response, es
from models import db, News, Urls
from flask import Flask, current_app, request, render_template, Response
from datetime import datetime

class FlaskAppHandler:
    def __init__(self, app, db):
        self.app = app
        self.db = db
        self.db.init_app(app)
        with self.app.app_context():
            self.db.create_all()
        self.register_routes()

    def register_routes(self):
        @self.app.route('/add')
        def add_data():
            with open('results.json') as f:
                data = json.load(f)
            # Loop through articles and add/update them in the database
            for article_data in data['Results']:
                if db.session.query(News).filter_by(url=article_data['url']).first():
                    print(f"Article with URL {article_data['url']} already exists in database.")
                    continue
                
                # Create new article if it doesn't exist in the database
                article = News(
                    source_domain=article_data['source_domain'],
                    authors=', '.join(article_data.get('authors', [])),
                    title=article_data['title'],
                    url=article_data['url'],
                    imageUrl=article_data['image_url'],
                    date= datetime.fromisoformat(article_data['date_publish']) if article_data['date_publish'] is not None else None,
                    content=article_data['maintext']
                )
                db.session.add(article)
            db.session.commit()
            index_articles(es)
            return success_response("added all data.")

        @self.app.route("/addurls")
        def addurls():
            # scrape_google_scholar_metadata(self)
            addNewsUrl(self)
            return success_response({"urls": [c.serialize() for c in Urls.query.all()]})

        @self.app.route("/news")
        def get_news():
            return Response(json.dumps({"news": [c.serialize() for c in News.query.all()]}),200)

        @self.app.route("/urls")
        def get_urls():
            return Response(json.dumps({"urls": [c.serialize() for c in Urls.query.all()]}), 200)

        @self.app.route('/query', methods=['POST'])
        def query():
            search_query = request.json['search_query']
            # Note, to change the query parameters, change the query dictionary.
            query = {
                "function_score": {
                    "query": {
                        "match": {
                            "content": search_query
                        },
                    },
                    "functions": [
                        {
                            "exp": {
                                "date": {
                                    "scale": "30d",
                                    "decay": 0.5
                                }
                            }
                        }
                    ]
                }
            }

            # Execute the search query
            es_result = es.search(index="articles", query=query)
            article_ids = [hit['_source']['title'] for hit in es_result['hits']['hits']]
            # Fetch the articles from the database
            articles = News.query.filter(News.title.in_(article_ids)).all()
            response = Response(json.dumps({"news": [article.serialize() for article in articles]}), 200)
            response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173' 

            return response


    def run(self, host="0.0.0.0", port=5000, debug=True):
        self.app.run(host=host, port=port, debug=debug)