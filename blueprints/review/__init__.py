import random, logging
from blueprints import db
from datetime import datetime
from flask_restful import fields

class Review(db.Model):
    __tablename__ = "review"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    cafeShopId = db.Column(db.Integer)
    cafeShopName = db.Column(db.String(200))
    cafeUserId = db.Column(db.Integer)
    cafeUserName = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    review = db.Column(db.String(200))


    response_field = {
        "id" : fields.Integer,
        "cafeShopId" : fields.Integer,
        "cafeShopName" : fields.String,
        "cafeUserId" : fields.Integer,
        "cafeUserName" : fields.String,
        "rating" : fields.Integer,
        "review" : fields.String
    }

    def __init__ (self, id, cafeShopId, cafeShopName, cafeUserId, cafeUserName, rating, review):
        self.id = id
        self.cafeShopId = cafeShopId
        self.cafeShopName = cafeShopName
        self.cafeUserId = cafeUserId
        self.cafeUserName = cafeUserName
        self.rating = rating
        self.review = review

    def __repr__(self):
        return f'<Review {self.id}>'


db.create_all()