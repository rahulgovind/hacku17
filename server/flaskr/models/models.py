from flask_sqlalchemy import SQLAlchemy
import re

db = SQLAlchemy()


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    keywords = db.Column(db.String(120), unique=True)

    def __init__(self, name, keywords):
        self.name = name
        self.keywords = keywords

    @property
    def keyword_list(self):
        return re.split('\n+|,', self.keywords)

    def __repr__(self):
        return '<Profile %r>' % self.name