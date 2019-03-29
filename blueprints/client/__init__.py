import random, logging
from blueprints import db
from flask_restful import fields

class Clients(db.Model):

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    mode = db.Column(db.String(100))
    lokasi = db.Column(db.String(100))


    response_field = {
        "id" : fields.Integer,
        "username" : fields.String,
        "password" : fields.String,
        "mode" : fields.String,
        "lokasi" : fields.String
    }

    def __init__ (self, id, username, password, mode, lokasi):
        self.id = id
        self.username = username
        self.password = password
        self.mode = mode
        self.lokasi = lokasi

    def __repr__(self):
        return f'<Client {self.id}>'

db.create_all()