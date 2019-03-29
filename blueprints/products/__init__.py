import random, logging
from blueprints import db
from datetime import datetime
from flask_restful import fields

class Products(db.Model):

    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Integer)
    urlPicture = db.Column(db.String(200), default="")
    coffeShopId = db.Column(db.Integer)
    coffeShopName = db.Column(db.String(200))
    

    response_field = {
        "id" : fields.Integer,
        "name" : fields.String,
        "price" : fields.Integer,
        "urlPicture" : fields.String,
        "coffeShopId" : fields.Integer,
        "coffeShopName" : fields.String
    }

    def __init__ (self, id, name, price, urlPicture, coffeShopId, coffeShopName):
        self.id = id
        self.name = name
        self.price = price
        self.urlPicture = urlPicture
        self.coffeShopId = coffeShopId
        self.coffeShopName = coffeShopName

    def __repr__(self):
        return f'<Products {self.id}>'


db.create_all()