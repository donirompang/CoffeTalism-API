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
    

    response_field = {
        "id" : fields.Integer,
        "name" : fields.String,
        "cafeShopId" : fields.Integer,
        "cafeShopName" : fields.String
    }

    def __init__ (self, id, name, cafeShopId, cafeShopName):
        self.id = id
        self.name = name
        self.cafeShopId = cafeShopId
        self.cafeShopName = cafeShopName

    def __repr__(self):
        return f'<Beans {self.id}>'


db.create_all()