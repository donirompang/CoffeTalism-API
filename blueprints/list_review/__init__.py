import random, logging
from blueprints import db
from flask_restful import fields

class ListReview(db.Model):

    __tablename__ = "list_review"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    userId = db.Column(db.Integer)
    cafeId = db.Column(db.Integer)
    reviewed = db.Column(db.String(100), default="tidak")

    response_field = {
        "id" : fields.Integer,
        "userId" : fields.Integer,
        "cafeId" : fields.Integer,
        "reviewed" : fields.String
    }

    def __init__ (self, id, userId, cafeId, reviewed):
        self.id = id
        self.userId = userId
        self.cafeId = cafeId
        self.reviewed = reviewed

    def __repr__(self):
        return f'<ListReview {self.id}>'

db.create_all()