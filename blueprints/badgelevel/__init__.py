import random, logging
from blueprints import db
from datetime import datetime
from flask_restful import fields

class BadgeLevel(db.Model):

    __tablename__ = "badgelevel"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    status = db.Column(db.String(200))
    point = db.Column(db.Integer)
    userId = db.Column(db.Integer)
    
    response_field = {
        "id" : fields.Integer,
        "status" : fields.String,
        "point" : fields.Integer,
        "userId" : fields.Integer
    }

    def __init__ (self, id, status, point, userId):
        self.id = id
        self.status = status
        self.point = point
        self.userId = userId
        

    def __repr__(self):
        return f'<BadgeLevel {self.id}>'


db.create_all()