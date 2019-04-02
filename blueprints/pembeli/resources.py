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
from blueprints.review import *
from blueprints.list_review import *
from sqlalchemy import func, or_

from math import sin, cos, sqrt, atan2, radians


bp_pembeli = Blueprint('pembeli', __name__)
api = Api(bp_pembeli)


def get_distance(lat1, lon1, lat2, lon2):
    R = 6373.0
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c * 1000
    return distance


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



class CariCafeBeanTerdekat(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('keyword', location='json', default=" ")
        parser.add_argument('latitude', location='json', type=float, default=0)
        parser.add_argument('longitude', location='json', type=float, default=0)

        args = parser.parse_args()

        list_cafe_terdekat = []

        list_cafe_id = []

        penjual = Penjual.query.filter(Penjual.name.like('%'+ args['keyword'] +'%')).all()

        hasil_cari = Beans.query.filter(Beans.name.like('%'+ args['keyword'] +'%')).all()

        for row in hasil_cari:
            if row.cafeShopId not in list_cafe_id:
                list_cafe_id.append(row.cafeShopId)


        for row in penjual:
            if row.id not in list_cafe_id:
                list_cafe_id.append(row.id)


        for row in list_cafe_id:
            penjual = Penjual.query.get(row)
            # lokasi = penjual.location.split('#')
            lokasi = [12.656511, -122.232131]
            lat_penjual = lokasi[0]
            lon_penjual = lokasi[1]
            tmp_dist = get_distance(args['latitude'], args['longitude'], lat_penjual, lon_penjual)
            list_cafe_terdekat.append([marshal(penjual, Penjual.response_field), tmp_dist])

        for i in range(len(list_cafe_terdekat)):
            for j in range(len(list_cafe_terdekat)):
                if(list_cafe_terdekat[i][1] < list_cafe_terdekat[j][1]):
                    tmp = list_cafe_terdekat[i]
                    list_cafe_terdekat[i] = list_cafe_terdekat[j]
                    list_cafe_terdekat[j] = tmp


        resp = {}
        resp['status'] = 404
        resp['results'] = []
        if len(list_cafe_terdekat) > 0:
            resp['status'] = 200
            resp['results'] = list_cafe_terdekat

        return resp, 200, { 'Content-Type': 'application/json' }
        
        

class CariBeans(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('keyword', location='json', default=" ")

        args = parser.parse_args()

        list_cafe = []

        qry = Beans.query.filter(Beans.name.like("%"+args['keyword']+"%")).all()
        for row in qry:
            cafeId = row.cafeShopId
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




class GetUserInfo(Resource):
    @jwt_required
    def get(self):
        userId = get_jwt_claims()['id']
        qry = Pembeli.query.get(userId)
        resp = {}
        if qry:
            resp['status'] = 200
            resp['results'] = marshal(qry, Pembeli.response_field)
            return resp, 200, { 'Content-Type': 'application/json' }
        resp['status'] = 404
        resp['results'] = {}
        return resp, 200, { 'Content-Type': 'application/json' }



class GetListCafeForReview(Resource):
    @jwt_required
    def get(self):
        userId = get_jwt_claims()['id']
        qry = ListReview.query.filter_by(userId = userId).filter_by(reviewed = 'tidak').all()
        list_cafe = []
        resp = {}
        resp['status'] = 404
        resp['results'] = list_cafe
        if qry:
            for row in qry:
                penjual = Penjual.query.get(row.cafeId)
                cafe = marshal(penjual, Penjual.response_field)
                list_cafe.append(cafe)
            resp['status'] = 200
            resp['results'] = list_cafe
        return resp, 200, { 'Content-Type': 'application/json' }

   

class GetRecentCafe(Resource):
    @jwt_required
    def get(self):
        userId = get_jwt_claims()['id']
        qry = History.query.filter_by(userId = userId).order_by(History.id.desc()).limit(6).all()
        list_cafe = []
        resp = {}
        if qry:
            for row in qry:
                penjual = Penjual.query.get(row.cafeId)
                cafe = marshal(penjual, Penjual.response_field)
                list_cafe.append(cafe)
            resp['status'] = 200
            resp['results'] = list_cafe
            return resp, 200, { 'Content-Type': 'application/json' }

        resp['status'] = 404
        resp['results'] = list_cafe
        return resp, 200, { 'Content-Type': 'application/json' }


# BAGIAN HISTORY


class GetHistory(Resource):
    @jwt_required
    def get(self):
        userId = get_jwt_claims()['id']
        qry = History.query.filter_by(userId = userId).order_by(History.created.desc()).all()
        list_cafe = []
        resp = {}
        if qry is not None:
            for row in qry:
                cafeId = row.cafeId
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
                cafeId = row.cafeId
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




class AddToListCafeForReview(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cafeId', location='json', type=int, required=True)
        
        args = parser.parse_args()
         
        userId = get_jwt_claims()['id']

        cafe_for_review = ListReview(None, userId, args['cafeId'], None)

        db.session.add(cafe_for_review)
        db.session.commit()

        return {"message" : "SUCCESS"}, 200, { 'Content-Type': 'application/json' }




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
            reviewHome = ListReview.query.filter_by(userId = cafeUserId).filter_by(cafeId = args['cafeShopId']).filter_by(reviewed = 'tidak').first()
            reviewHome.reviewed = 'ya'
            db.session.commit()
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
        parser.add_argument('cafeShopId', location='json', type=int, required=True)
        parser.add_argument('rating', location='json', type=int, required=True)
        parser.add_argument('review', location='json', required=True)


        args = parser.parse_args()
        cafeUserId = get_jwt_claims()['id']
        cafe = Penjual.query.get(args['cafeShopId'])
        
        if cafe is not None:
            review = Review.query.filter_by(cafeUserId=cafeUserId).filter_by(cafeShopId=args['cafeShopId']).first()
            if review is not None:
                review.rating = args['rating']
                review.review = args['review']
                db.session.commit()
                return marshal(review,Review.response_field), 200, { 'Content-Type': 'application/json' }
            else:
                return {"message" : "Review Not Found"}, 404, { 'Content-Type': 'application/json' }
        return {"message" : "ID Cafe Not Found"}, 404, { 'Content-Type': 'application/json' }


class DeleteReview(Resource):
    @jwt_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cafeShopId', location='json', type=int, required=True)


        args = parser.parse_args()
        cafeUserId = get_jwt_claims()['id']
        cafe = Penjual.query.get(args['cafeShopId'])
        
        if cafe is not None:
            review = Review.query.filter_by(cafeUserId=cafeUserId).filter_by(cafeShopId=args['cafeShopId']).filter_by(deleted = 'tidak').first()
            if review is not None:
                review.deleted = "ya"
                db.session.commit()
                return {"Message" : "Deleted"}, 200, { 'Content-Type': 'application/json' }
            else:
                return {"message" : "Review Not Found"}, 404, { 'Content-Type': 'application/json' }
        return {"message" : "ID Cafe Not Found"}, 404, { 'Content-Type': 'application/json' }



class GetReview(Resource):
    @jwt_required
    def get(self):
        cafeUserId = get_jwt_claims()['id']
        qry = Review.query.filter_by(cafeUserId=cafeUserId).filter_by(deleted="tidak").all()
        list_review = []

        if qry is not None:
            for row in qry:
                review = marshal(row, Review.response_field)
                list_review.append(review)            

        resp = {}
        resp['status'] = 404
        resp['results'] = list_review
        if len(list_review) > 0:
            resp['status'] = 200
            resp['results'] = list_review
            return resp, 200, { 'Content-Type': 'application/json' }
        
        return resp, 200, { 'Content-Type': 'application/json' } 








class GetProfile(Resource):
    @jwt_required
    def get(self):
        UserId = get_jwt_claims()['id']
        qry = Pembeli.query.get(UserId)

        if qry is not None:
            profile = marshal(qry, Pembeli.response_field)        

        resp = {}
        resp['status'] = 404
        resp['results'] = profile
        if len(profile) > 0:
            resp['status'] = 200
            resp['results'] = profile
            return resp, 200, { 'Content-Type': 'application/json' }
        
        return resp, 200, { 'Content-Type': 'application/json' }



class AddPoint(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cafeId', location='json', type=int, required=True)

        args = parser.parse_args()
 
        userId = get_jwt_claims()['id']

        user = Pembeli.query.get(userId)
        if user is not None:
            user.point = user.point + 10
        else:
            return {"message" : "ID Cafe not found"}, 404, { 'Content-Type': 'application/json' }
        
        if user.point < 50 :
            user.bagde = 'Pemula Baru'
        elif user.point < 100:
            user.bagde = "Penikmat Cofee"
        elif user.point > 100:
            user.bagde = "Legendary"
        db.session.commit()

        return {"message" : "SUCCESS"}, 200, { 'Content-Type': 'application/json' }


api.add_resource(GetUserInfo, "/api/userinfo")
      
api.add_resource(CariCafe, "/api/cari/cafe")
api.add_resource(CariBeans, "/api/cari/beans")
api.add_resource(CariCafeBeanTerdekat, "/api/cari/terdekat")

api.add_resource(GetPopularCafe, "/api/popularcafe")
api.add_resource(GetRecentCafe, "/api/recentcafe")

api.add_resource(GetHistory, "/api/history/get")
api.add_resource(AddToHistory, "/api/history/add")

api.add_resource(GetFavoriteCafe, "/api/favorite/get")
api.add_resource(AddToFavorite, "/api/favorite/add")
api.add_resource(DeleteFavorite, "/api/favorite/delete")

api.add_resource(AddReview, "/api/review/add")

api.add_resource(GetListCafeForReview, "/api/review/cafelist")
api.add_resource(AddToListCafeForReview, "/api/review/addlist")


api.add_resource(UpdateReview, "/api/review/edit")
api.add_resource(DeleteReview, "/api/review/hapus")
api.add_resource(GetReview, "/api/review/get")

api.add_resource(GetProfile, "/api/profile/get")

api.add_resource(AddPoint, "/api/point/post")

