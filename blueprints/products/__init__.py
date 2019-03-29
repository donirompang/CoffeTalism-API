import random, logging
from blueprints import db
from datetime import datetime
from flask_restful import fields

class Products(db.Model):

    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Integer)
    urlPicture = db.Column(db.String(200), default="https://imgur.com/a/KY126k9")
    coffeeShopId = db.Column(db.Integer)
    coffeeShopName = db.Column(db.String(200))
    

    response_field = {
        "id" : fields.Integer,
        "name" : fields.String,
        "price" : fields.Integer,
        "urlPicture" : fields.String,
        "coffeeShopId" : fields.Integer,
        "coffeeShopName" : fields.String
    }

    def __init__ (self, id, name, price, urlPicture, coffeeShopId, coffeeShopName):
        self.id = id
        self.name = name
        self.price = price
        self.urlPicture = urlPicture
        self.coffeeShopId = coffeeShopId
        self.coffeeShopName = coffeeShopName

    def __repr__(self):
        return f'<Products {self.id}>'


db.create_all()