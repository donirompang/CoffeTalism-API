import random, logging
from blueprints import db
from datetime import datetime
from flask_restful import fields

class Beans(db.Model):

    __tablename__ = "beans"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    name = db.Column(db.String(200))
    cafeShopId = db.Column(db.Integer)
    cafeShopName = db.Column(db.String(200))
    photoUrl = db.Column(db.String(200))
    notes = db.Column(db.String(200))
    

    response_field = {
        "id" : fields.Integer,
        "name" : fields.String,
        "cafeShopId" : fields.Integer,
        "cafeShopName" : fields.String
        "photoUrl" : fields.String
        "notes" : fields.String
    }

    def __init__ (self, id, name, cafeShopId, cafeShopName, photoUrl, notes):
        self.id = id
        self.name = name
        self.cafeShopId = cafeShopId
        self.cafeShopName = cafeShopName
        self.photoUrl = photoUrl
        self.notes = notes

    def __repr__(self):
        return f'<Beans {self.id}>'


db.create_all()