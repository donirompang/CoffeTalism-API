import random, logging
from blueprints import db
from flask_restful import fields

class Pembeli(db.Model):

    __tablename__ = "pembeli"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    username = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    password = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    point = db.Column(db.Integer)
    bagde = db.Column(db.String(100))
    profilePicture = db.Column(db.String(100))
    status = db.Column(db.String(100), default="pembeli")


    response_field = {
        "id" : fields.Integer,
        "username" : fields.String,
        "name" : fields.String,
        "password" : fields.String,
        "email" : fields.String,
        "point" : fields.Integer,
        "bagde" : fields.String,
        "profilePicture" : fields.String,
        "status" : fields.String
    }

    def __init__ (self, id, username, name, password, email, point, bagde, profilePicture, status):
        self.id = id
        self.username = username
        self.name = name
        self.password = password
        self.email = email
        self.point = point
        self.bagde = bagde
        self.profilePicture = profilePicture
        self.status = status

    def __repr__(self):
        return f'<Pembeli {self.id}>'

db.create_all()