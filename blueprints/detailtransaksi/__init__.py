import random, logging
from blueprints import db
from datetime import datetime
from flask_restful import fields

class DetailTransaksi(db.Model):

    __tablename__ = "detailtransaksi"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    userId = db.Column(db.Integer, default=0)
    beanId = db.Column(db.Integer)
    totalTransaksi = db.Column(db.Integer)
    scanned = db.Column(db.String(200), default='tidak')
    

    response_field = {
        "id" : fields.Integer,
        "userId" : fields.Integer,
        "beanId" : fields.Integer,
        "totalTransaksi" : fields.Integer,
        "scanned" : fields.String
    }

    def __init__ (self, id, userId, beanId, totalTransaksi, scanned):
        self.id = id
        self.userId = userId
        self.beanId = beanId
        self.totalTransaksi = totalTransaksi
        self.scanned = scanned

    def __repr__(self):
        return f'<DetailTransaksi {self.id}>'


db.create_all()