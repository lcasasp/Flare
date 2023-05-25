from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class News(db.Model):
    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String)
    total_results = db.Column(db.Integer)
    source_id = db.Column(db.String)
    source_name = db.Column(db.String)
    author = db.Column(db.String)
    title = db.Column(db.String)
    description = db.Column(db.String)
    url = db.Column(db.String)
    url_to_image = db.Column(db.String)
    published_at = db.Column(db.String)
    content = db.Column(db.String)

    def serialize(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "source_name": self.source_name,
            "author": self.author,
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "url_to_image": self.url_to_image,
            "published_at": self.published_at,
            "content": self.content
        }
    

    def __init__(self, status, total_results, source_id, source_name, author,
     title, description, url, url_to_image, published_at, content):
        self.status = status
        self.total_results = total_results
        self.source_id = source_id
        self.source_name = source_name
        self.author = author
        self.title = title
        self.description = description
        self.url = url
        self.url_to_image = url_to_image
        self.published_at = published_at
        self.content = content