import random, logging
from blueprints import db
from flask_restful import fields

class Favorite(db.Model):

    __tablename__ = "favorite"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    userId = db.Column(db.Integer)
    cafeId = db.Column(db.Integer)
    cafeName = db.Column(db.String(100))
    deleted = db.Column(db.String(100), default="tidak")

    response_field = {
        "id" : fields.Integer,
        "userId" : fields.Integer,
        "cafeId" : fields.Integer,
        "cafeName" : fields.String,
        "deleted" : fields.String
    }

    def __init__ (self, id, userId, cafeId, cafeName, deleted):
        self.id = id
        self.userId = userId
        self.cafeId = cafeId
        self.cafeName = cafeName
        self.deleted = deleted

    def __repr__(self):
        return f'<Favorite {self.id}>'

db.create_all()