import random, logging
from blueprints import db
from flask_restful import fields
from datetime import datetime

class History(db.Model):

    __tablename__ = "history"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    userId = db.Column(db.Integer)
    cafeId = db.Column(db.Integer)
    cafeName = db.Column(db.String(100))
    created = db.Column(db.DateTime, default=datetime.utcnow)

    response_field = {
        "id" : fields.Integer,
        "userId" : fields.Integer,
        "cafeId" : fields.Integer,
        "cafeName" : fields.String,
        "created" : fields.DateTime(dt_format='rfc822')
    }

    def __init__ (self, id, userId, cafeId, cafeName, created):
        self.id = id
        self.userId = userId
        self.cafeId = cafeId
        self.cafeName = cafeName
        self.created = created

    def __repr__(self):
        return f'<History {self.id}>'

db.create_all()