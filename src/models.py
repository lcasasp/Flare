from sqlalchemy import ForeignKey, func
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class News(db.Model):
    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True, index=True)
    source_domain = db.Column(db.String)
    title = db.Column(db.String, unique=True, index=True)
    authors = db.Column(db.String)
    url = db.Column(db.String, unique=True, index=True)
    date = db.Column(db.DateTime)
    imageUrl = db.Column(db.String, default=None)
    is_indexed = db.Column(db.Boolean, default=False)
    content = db.Column(db.String)
    urls = db.relationship("Urls", back_populates="news")

    def serialize(self):
        print(f"Date before serialization: {self.date}")
        return {
            "id": self.id,
            "source_domain": self.source_domain,
            "title": self.title,
            "authors": self.authors,
            "url": self.url,
            "date": self.date.isoformat() if self.date is not None else None,
            "imageUrl": self.imageUrl,
            "is_indexed": self.is_indexed,
            "content": self.content
        }

    def mark_as_indexed(self):
        self.is_indexed = True
        db.session.commit()


class Urls(db.Model):
    __tablename__ = 'urls'

    id = db.Column(db.Integer, primary_key=True, index=True)
    url = db.Column(db.String, unique=True, index=True)
    is_scraped = db.Column(db.Boolean, default=False)
    news_id = db.Column(db.Integer, ForeignKey('news.id'))
    news = db.relationship("News", back_populates="urls")

    def serialize(self):
        return {
            "id": self.id,
            "url": self.url,
            "is_scraped": self.is_scraped,
            "news_id": self.news_id
        }

    def mark_as_scraped(self):
        self.is_scraped = True
        db.session.commit()
