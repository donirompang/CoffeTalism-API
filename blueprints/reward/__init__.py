import random, logging
from blueprints import db
from datetime import datetime
from flask_restful import fields

class Reward(db.Model):
    __tablename__ = "reward"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    cafeShopId = db.Column(db.Integer)
    cafeUserId = db.Column(db.Integer)
    code = db.Column(db.String(10))
    desc = db.Column(db.String(200))
    status = db.Column(db.String(100), default="unused")


    response_field = {
        "id" : fields.Integer,
        "cafeShopId" : fields.Integer,
        "cafeUserId" : fields.Integer,
        "code" : fields.String,
        "desc" : fields.String,
        "status" : fields.String
    }

    def __init__ (self, id, cafeShopId, cafeUserId, code, desc, status):
        self.id = id
        self.cafeShopId = cafeShopId
        self.cafeUserId = cafeUserId
        self.code = code
        self.desc = desc
        self.status = status

    def __repr__(self):
        return f'<Reward {self.id}>'


db.create_all()