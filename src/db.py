from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class News(db.Model):
    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True)
    source_domain = db.Column(db.String)
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
            "source_domain": self.source_domain,
            "author": self.author,
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "url_to_image": self.url_to_image,
            "published_at": self.published_at,
            "content": self.content
        }
    
    def __init__(self, source_domain, author,
     title, description, url, url_to_image, published_at, content):
        self.source_domain = source_domain
        self.author = author
        self.title = title
        self.description = description
        self.url = url
        self.url_to_image = url_to_image
        self.published_at = published_at
        self.content = content


class Urls(db.Model):
    __tablename__ = 'urls'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String)

    def serialize(self):
        return {
            "id": self.id,
            "url": self.url,
        }
    
    def __init__(self, url):
        self.url = url