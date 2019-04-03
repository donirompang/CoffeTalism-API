import random, logging
from blueprints import db
from flask_restful import fields

class Penjual(db.Model):

    __tablename__ = "penjual"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    rating = db.Column(db.Integer)
    photo = db.Column(db.String(100))
    location = db.Column(db.String(255))
    status = db.Column(db.String(100), default="penjual")


    response_field = {
        "id" : fields.Integer,
        "username" : fields.String,
        "password" : fields.String,
        "name" : fields.String,
        "email" : fields.String,
        "rating" : fields.Integer,
        "photo" : fields.String,
        "location" : fields.String,
        "status" : fields.String
    }

    def __init__ (self, id, username, password, name, email, rating, photo, location, status):
        self.id = id
        self.username = username
        self.password = password
        self.name = name
        self.email = email
        self.rating = rating
        self.photo = photo
        self.location = location
        self.status = status

    def __repr__(self):
        return f'<Penjual {self.id}>'

db.create_all()