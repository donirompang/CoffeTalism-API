import logging, json
from flask import Blueprint, render_template, abort, request
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from flask_jwt_extended import jwt_required, get_jwt_claims
from jinja2 import TemplateNotFound
from datetime import datetime
from . import *
from blueprints.favorite import *
from blueprints.history import *
from blueprints.beans import *
from blueprints.penjual import *
from sqlalchemy import func

bp_pembeli = Blueprint('pembeli', __name__)
api = Api(bp_pembeli)

class CariCafe(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('keyword', location='json', default=" ")

        args = parser.parse_args()

        list_cafe = []

        qry = Penjual.query.filter(Penjual.name.like("%"+args['keyword']+"%")).all()
        for row in qry:
            cafe = marshal(row, Penjual.response_field)
            list_cafe.append(cafe)            

        resp = {}
        resp['status'] = 404
        resp['results'] = list_cafe
        if len(list_cafe) > 0:
            resp['status'] = 200
            resp['results'] = list_cafe
            return resp, 200, { 'Content-Type': 'application/json' }
        
        return resp, 200, { 'Content-Type': 'application/json' }



class CariBeans(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('keyword', location='json', default=" ")

        args = parser.parse_args()

        list_cafe = []

        qry = Beans.query.filter(Beans.name.like("%"+args['keyword']+"%")).all()
        for row in qry:
            cafeId = row.cafeId
            penjual = Penjual.query.get(cafeId)
            cafe = marshal(penjual, Penjual.response_field)
            list_cafe.append(cafe)            

        resp = {}
        resp['status'] = 404
        resp['results'] = list_cafe
        if len(list_cafe) > 0:
            resp['status'] = 200
            resp['results'] = list_cafe
            return resp, 200, { 'Content-Type': 'application/json' }
        
        return resp, 200, { 'Content-Type': 'application/json' }



# by cafe rating
class GetPopularCafe(Resource):
    def get(self):
        qry = Penjual.query.order_by(Penjual.rating.desc()).limit(6).all()
        list_cafe = []
        resp = {}
        if qry:
            for row in qry:
                cafe = marshal(row,Penjual.response_field)
                list_cafe.append(cafe)
            resp['status'] = 200
            resp['results'] = list_cafe
            return resp, 200, { 'Content-Type': 'application/json' }
        resp['status'] = 404
        resp['results'] = list_cafe
        return resp, 404, { 'Content-Type': 'application/json' }


# BAGIAN HISTORY
class GetHistory(Resource):
    @jwt_required
    def get(self):
        userId = get_jwt_claims()['id']
        qry = History.query.filter_by(userId = userId).order_by(History.created.desc()).all()
        list_cafe = []
        resp = {}
        if qry:
            for row in qry:
                cafeId = qry.cafeId
                penjual = Penjual.query.get(cafeId)
                cafe = marshal(penjual,Penjual.response_field)
                list_cafe.append(cafe)
            resp['status'] = 200
            resp['results'] = list_cafe
            return resp, 200, { 'Content-Type': 'application/json' }
        resp['status'] = 404
        resp['results'] = list_cafe
        return resp, 404, { 'Content-Type': 'application/json' }



class AddToHistory(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cafeId', location='json', type=int, required=True)
        
        args = parser.parse_args()
 
        userId = get_jwt_claims()['id']

        cafe = Penjual.query.get(args['cafeId'])
        if cafe is not None:
            history = History(None, userId, args['cafeId'], cafe.name, None)
        else:
            return {"message" : "ID Cafe not found"}, 404, { 'Content-Type': 'application/json' }

        db.session.add(history)
        db.session.commit()

        return {"message" : "SUCCESS"}, 200, { 'Content-Type': 'application/json' }


# BAGIAN FAVORITE
class GetFavoriteCafe(Resource):
    @jwt_required
    def get(self):
        userId = get_jwt_claims()['id']
        qry = Favorite.query.filter_by(userId = userId).all()
        list_cafe = []
        resp = {}
        if qry:
            for row in qry:
                cafeId = qry.cafeId
                penjual = Penjual.query.get(cafeId)
                cafe = marshal(penjual,Penjual.response_field)
                list_cafe.append(cafe)
            resp['status'] = 200
            resp['results'] = list_cafe
            return resp, 200, { 'Content-Type': 'application/json' }
        resp['status'] = 404
        resp['results'] = list_cafe
        return resp, 404, { 'Content-Type': 'application/json' }



class AddToFavorite(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cafeId', location='json', type=int, required=True)
        
        args = parser.parse_args()

         
        userId = get_jwt_claims()['id']


        cafe = Penjual.query.get(args['cafeId'])
        if cafe is not None:
            favorite = Favorite(None, userId, args['cafeId'], cafe.name, None)
        else:
            return {"message" : "ID cafe not found"}, 404, { 'Content-Type': 'application/json' }

        db.session.add(favorite)
        db.session.commit()

        return {"message" : "SUCCESS"}, 200, { 'Content-Type': 'application/json' }



class DeleteFavorite(Resource):
    @jwt_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cafeId', location='json', type=int, required=True)
        
        args = parser.parse_args()

        userId = get_jwt_claims()['id']
        favorite = Favorite.query.filter_by(userId=userId).filter_by(cafeId=args['cafeId']).filter_by(deleted = 'tidak').first()
        
        if favorite is not None:
            favorite.deleted = "ya"
            db.session.commit()
            return {"Message" : "Deleted"}, 200, { 'Content-Type': 'application/json' }
        return {"message" : "Not Found"}, 404, { 'Content-Type': 'application/json' }



#BAGIAN ADD Review
class AddReview(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cafeShopId', location='json', type=int, required=True)
        parser.add_argument('rating', location='json', type=int, required=True)
        parser.add_argument('review', location='json', required=True)

        
        args = parser.parse_args()

         
        cafeUserId = get_jwt_claims()['id']
        cafeUserName = get_jwt_claims()['name']

        cafe = Penjual.query.get(args['cafeShopId'])
        if cafe is not None:
            review = Review(None, args['cafeShopId'], cafe.name, cafeUserId, cafeUserName, args['rating'], args['review'])
        else:
            return {"message" : "ID Cafe not found"}, 404, { 'Content-Type': 'application/json' }

        db.session.add(review)
        db.session.commit()

        return {"message" : "SUCCESS"}, 200, { 'Content-Type': 'application/json' }



class UpdateReview(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('rating', location='json', type=int, required=True)
        parser.add_argument('review', location='json', required=True)


        args = parser.parse_args()
        cafeUserId = get_jwt_claims()['id']
        cafe = Penjual.query.get(args['cafeShopId'])
        
        if cafe is not None:
            review = Review.query.filter_by(cafeUserId=cafeUserId)
            if barang is not None:
                cart_detail.qty = args['qty']
                cart_detail.price = barang.harga
                db.session.commit()
                return marshal(cart_detail,CartDetail.response_field), 200, { 'Content-Type': 'application/json' }
            else:
                return {"message" : "ID Barang Not Found"}, 404, { 'Content-Type': 'application/json' }
        return {"message" : "Cart Item Not Found"}, 404, { 'Content-Type': 'application/json' }


api.add_resource(CariCafe, "/api/cari/cafe")
api.add_resource(CariBeans, "/api/cari/beans")

api.add_resource(GetPopularCafe, "/api/popularcafe")

api.add_resource(GetHistory, "/api/history/get")
api.add_resource(AddToHistory, "/api/history/add")

api.add_resource(GetFavoriteCafe, "/api/favorite/get")
api.add_resource(AddToFavorite, "/api/favorite/add")
api.add_resource(DeleteFavorite, "/api/favorite/delete")

api.add_resource(AddReview, "api/review/add")
# api.add_resource(AddReview, "api/review/edit")
# api.add_resource(AddReview, "api/review/hapus")