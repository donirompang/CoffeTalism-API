import logging, json
from flask import Blueprint,render_template
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_claims

from blueprints.penjual import *
from blueprints.products import *
from blueprints.beans import *
from blueprints.review import *
from blueprints.detailtransaksi import *
from blueprints.favorite import *
from blueprints.pembeli import *
from blueprints.reward import *

bp_penjual = Blueprint('penjual', __name__)
api = Api(bp_penjual)

class addProduct(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('productname', location='json', required=True)
        parser.add_argument('price', location='json', type=int, required=True)
        parser.add_argument('photo', location='json')
        parser.add_argument('deskripsi', location='json')

        args = parser.parse_args()
        penjual = get_jwt_claims()
 
        new_bean = Products(None, args['productname'], args['price'], args['photo'], penjual['id'], penjual['name'], args['deskripsi'] )
        db.session.add(new_bean)
        db.session.commit()
        resp = {}
        resp['status'] = 200
        resp['bean'] = marshal(new_bean, Products.response_field)
        return resp, 200, { 'Content-Type': 'application/json' }

class editProduct(Resource):
    @jwt_required
    def put(self):
        penjual = get_jwt_claims()
        parser = reqparse.RequestParser()
        parser.add_argument('idProduct', location='json', type=int, required=True)
        parser.add_argument('productname', location='json', default=None)
        parser.add_argument('price', location='json', type=int, default=None)
        parser.add_argument('photo', location='json', default=None)

        args = parser.parse_args()
        qry_product = Products.query.filter_by(coffeeShopId=penjual['id']).filter_by(id=args['idProduct']).first()

        if qry_product is None:
            return {'Message': 'product tidak ditemukan'}, 404, {'Content-Type': 'application/json'}

        else:
            if args['productname'] is not None:
                qry_product.name = args['productname']

            if args['price'] is not None:
                qry_product.price =args['price']

            if args['photo'] is not None:
                qry_product.urlPicture =args['photo']
            
            db.session.commit()
            resp = {}
            resp['status'] = 200
            resp['result'] = marshal (qry_product, Products.response_field)
            return resp, 200, { 'Content-Type': 'application/json' }

class deleteProduct(Resource):
    @jwt_required
    def delete(self, idProduct):
        penjual = get_jwt_claims()

        qry_product = Products.query.filter_by(coffeeShopId=penjual['id']).filter_by(id=idProduct).first()

        if qry_product is not None:
            db.session.delete(qry_product)
            db.session.commit()
            return {'status': 200}, 200, {'Content-Type': 'application/json'}
        return {'status': 404}, 404, {'Content-Type': 'application/json'}

class getProduct(Resource):
    @jwt_required
    def get(self):
        penjual_id = get_jwt_claims()['id']
        qry = Products.query.filter_by(coffeeShopId = penjual_id).all()
        listProduct = []
        resp = {}
        resp['status'] = 404
        resp['results'] = []
        if qry:
            for row in qry:
                product = marshal(row, Products.response_field)
                listProduct.append(product)
            resp['status'] = 200
            resp['results'] = listProduct
        return resp, 200, { 'Content-Type': 'application/json' }

class getProductId(Resource):
    @jwt_required
    def get(self, idProduct):
        penjual_id = get_jwt_claims()['id']
        qry = Products.query.filter_by(coffeeShopId = penjual_id).filter_by(id=idProduct).first()
        resp = {}
        resp['status'] = 404
        resp['results'] = []
        if qry:
            product = marshal(qry, Products.response_field)
            resp['status'] = 200
            resp['results'] = product
        return resp, 200, { 'Content-Type': 'application/json' }

class addBeans(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('coffeename', location='json', required=True)
        parser.add_argument('photo', location='json')
        parser.add_argument('notes', location='json', default=None)
        parser.add_argument('tipe', location='json', default='Beans Lokal')

        args = parser.parse_args()
        penjual = get_jwt_claims()
        new_bean = Beans(None, args['coffeename'], penjual['id'], penjual['name'], args['photo'], args['notes'], args['tipe']  )
        db.session.add(new_bean)
        db.session.commit()
        resp = {}
        resp['status'] = 200
        resp['bean'] = marshal(new_bean, Beans.response_field)
        return resp, 200, { 'Content-Type': 'application/json' }

class editBeans(Resource):
    @jwt_required
    def put(self):
        penjual = get_jwt_claims()
        parser = reqparse.RequestParser()
        parser.add_argument('idBeans', location='json', type=int, required=True)
        parser.add_argument('coffeename', location='json', default=None)
        parser.add_argument('photo', location='json', default=None)
        parser.add_argument('notes', location='json', default=None)

        args = parser.parse_args()

        qry_product = Beans.query.filter_by(cafeShopId=penjual['id']).filter_by(id=args['idBeans']).first()


        if qry_product is None:
            return {'Message': 'beans tidak ditemukan'}, 404, {'Content-Type': 'application/json'}

        else:
            if args['coffeename'] is not None:
                qry_product.name = args['coffeename']

            if args['photo'] is not None:
                qry_product.photoUrl =args['photo']
            
            if args['notes'] is not None:
                qry_product.notes =args['notes']
            
            db.session.commit()
            resp = {}
            resp['status'] = 200
            resp['result'] = marshal (qry_product, Beans.response_field)
            return resp, 200, { 'Content-Type': 'application/json' }

class deleteBeans(Resource):
    @jwt_required
    def delete(self, idProduct):
        penjual = get_jwt_claims()

        qry_product = Beans.query.filter_by(cafeShopId=penjual['id']).filter_by(id=idProduct).first()

        if qry_product is not None:
            db.session.delete(qry_product)
            db.session.commit()
            return {'status': 200}, 200, {'Content-Type': 'application/json'}
        return {'status': 404}, 404, {'Content-Type': 'application/json'}

class getBeans(Resource):
    @jwt_required
    def get(self):
        penjual_id = get_jwt_claims()['id']
        qry = Beans.query.filter_by(cafeShopId = penjual_id).all()
        listProduct = []
        resp = {}
        resp['status'] = 404
        resp['results'] = []
        if qry:
            for row in qry:
                product = marshal(row, Beans.response_field)
                listProduct.append(product)
            resp['status'] = 200
            resp['results'] = listProduct
        return resp, 200, { 'Content-Type': 'application/json' }

class getBeansId(Resource):
    @jwt_required
    def get(self, idBeans):
        penjual_id = get_jwt_claims()['id']
        qry = Beans.query.filter_by(cafeShopId = penjual_id).filter_by(id = idBeans).first()
        resp = {}
        resp['status'] = 404
        resp['results'] = []
        if qry:
            bean = marshal(qry, Beans.response_field)
            resp['status'] = 200
            resp['results'] = bean
        return resp, 200, { 'Content-Type': 'application/json' }

class getReview(Resource):
    @jwt_required
    def get(self):
        penjual_id = get_jwt_claims()['id']
        qry = Review.query.filter_by(cafeShopId = penjual_id).all()
        listReview = []
        resp = {}
        resp['status'] = 404
        resp['results'] = []
        if qry:
            for row in qry:
                review = marshal(row, Review.response_field)
                listReview.append(review)
            resp['status'] = 200
            resp['results'] = listReview
        return resp, 200, { 'Content-Type': 'application/json' }


class getProfil(Resource):
    @jwt_required
    def get(self):
        penjual = get_jwt_claims()
        qry = Penjual.query.get(penjual['id'])
        print(qry)
        resp = {}
        resp['status'] = 404
        resp['results'] = ""
        if qry:
            review = marshal(qry, Penjual.response_field)
            resp['status'] = 200
            resp['results'] = review
        return resp, 200, { 'Content-Type': 'application/json' }

class EditProfilePenjual(Resource):
    @jwt_required
    def put(self):
        penjual = get_jwt_claims()
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json', default=None)
        parser.add_argument('photo', location='json', default=None)
        parser.add_argument('password', location='json', default=None)
        parser.add_argument('k_password', location='json', default=None)

        args = parser.parse_args()
        qry_penjual = Penjual.query.filter_by(id=penjual['id']).first()

        if args['password'] != args['k_password']:
            return {'Message': 'Password dan Konfirmasi tidak cocok.'}, 200, {'Content-Type': 'application/json'}

        if qry_penjual is None:
            return {'Message': 'user belum terdaftar'}, 404, {'Content-Type': 'application/json'}

        else:
            if args['name'] is not None:
                qry_penjual.name =args['name']

            if args['photo'] is not None:
                qry_penjual.photo =args['photo']

            if args['password'] is not None:
                qry_penjual.password = args['password']
            
            db.session.commit()
            resp = {}
            resp['status'] = 200
            resp['result'] = marshal (qry_penjual, Penjual.response_field)
            return resp, 200, { 'Content-Type': 'application/json' }


class AddDetailTransaksi(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('beanId', location='json', type=int, required=True)
        parser.add_argument('totalTransaksi', location='json', type=int, required=True)

        args = parser.parse_args()
 
        shopId = get_jwt_claims()['id']

        tx = DetailTransaksi(None, None, args['beanId'], args['totalTransaksi'], None)
        
        db.session.add(tx)
        db.session.commit()
        
        resp = {}
        resp['status'] = 200
        resp['results'] = marshal(tx, DetailTransaksi.response_field)

        return resp, 200, { 'Content-Type': 'application/json' }


class GetFavoriteToken(Resource):
    @jwt_required
    def get(self):
        penjualId = get_jwt_claims()['id']
        qry = Favorite.query.filter_by(cafeId = penjualId).filter_by(deleted = 'tidak').all()
        list_token = []
        resp = {}
        resp['status'] = 404
        resp['results'] = list_token
        if qry is not None:
            for row in qry:
                pembeli = Pembeli.query.get(row.userId)
                list_token.append(pembeli.pushToken)
            resp['status'] = 200
        
        return resp, 200, { 'Content-Type': 'application/json' }

class RedeemRewardVoucher(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('code', location='json', required=True)

        args = parser.parse_args()
 
        cafeShopId = get_jwt_claims()['id']

        qry = Reward.query.filter_by(code = args['code']).first()
        
        if qry is None:
            return {'Message': 'Code tidak ditemukan'}, 404, {'Content-Type': 'application/json'}

        elif args['status'] == 'used':
            return {'Message': 'Code tidak ditemukan'}, 404, {'Content-Type': 'application/json'}
        else:
            qry.cafeShopId = cafeShopId
            qry.status = "used"
            db.session.commit()
            resp = {}
            resp['status'] = 200
            resp['result'] = marshal (qry, Reward.response_field)
            return resp, 200, { 'Content-Type': 'application/json' }

class getAllRedeemRewardVoucher(Resource):
    @jwt_required
    def get(self):
        penjual_id = get_jwt_claims()['id']
        qry = Reward.query.filter_by(cafeShopId = penjual_id).all()
        listReward = []
        resp = {}
        resp['status'] = 404
        resp['results'] = []
        if qry:
            for row in qry:
                reward = marshal(row, Beans.response_field)
                listReward.append(reward)
            resp['status'] = 200
            resp['results'] = listProduct
        return resp, 200, { 'Content-Type': 'application/json' }


class GetAllPushToken(Resource):
    @jwt_required
    def get(self):
        penjualId = get_jwt_claims()['id']
        qry = Pembeli.query.filter_by().all()
        list_token = []
        resp = {}
        resp['status'] = 404
        resp['results'] = list_token
        if qry is not None:
            for row in qry:
                list_token.append(row.pushToken)
            resp['status'] = 200
        
        return resp, 200, { 'Content-Type': 'application/json' }


class GetDetailCafe(Resource):
    @jwt_required
    def get(self):
        cafeId = get_jwt_claims()['id']
        qry = Penjual.query.filter_by(id = cafeId).first()
        qryBeans = Beans.query.filter_by(cafeShopId = cafeId).all()
        qryProduct = Products.query.filter_by(coffeeShopId = cafeId).all()
        qryReview = Review.query.filter_by(cafeShopId = cafeId).all()
        list_beans = []
        list_product = []
        list_review = []
        cafe = marshal(qry, Penjual.response_field)
        resp = {}

        if qryBeans:
            for row in qryBeans:
                beans = marshal(row, Beans.response_field)
                list_beans.append(beans)
        if qryProduct:
            for row in qryProduct:
                products = marshal(row, Products.response_field) 
                list_product.append(products)
        if qryReview:
            for row in qryReview:
                reviews = marshal(row, Review.response_field)
                list_review.append(reviews)
        resp['status'] = 200
        resp['results'] = {}
        resp['results']['cafe'] = cafe
        resp['results']['beans'] = list_beans
        resp['results']['product'] = list_product
        resp['results']['review'] = list_review
        return resp, 200, { 'Content-Type': 'application/json' }


api.add_resource(GetDetailCafe, "/api/profile")

api.add_resource(EditProfilePenjual, "/api/profile/edit")
api.add_resource(addProduct, "/api/product/tambah")
api.add_resource(editProduct, "/api/product/edit")
api.add_resource(deleteProduct, "/api/product/delete/<int:idProduct>")
api.add_resource(getProduct, "/api/product/get")
api.add_resource(getProductId, "/api/product/get/<int:idProduct>")
api.add_resource(addBeans, "/api/beans/tambah")
api.add_resource(editBeans, "/api/beans/edit")
api.add_resource(deleteBeans, "/api/beans/delete/<int:idProduct>")
api.add_resource(getBeans, "/api/beans/get")

api.add_resource(RedeemRewardVoucher, "/api/reward/put")
api.add_resource(getAllRedeemRewardVoucher, "/api/reward/get")

api.add_resource(getProfil, "/api/profil/get")
api.add_resource(getReview, "/api/review/get")

api.add_resource(getBeansId, "/api/beans/get/<int:idBeans>")


api.add_resource(AddDetailTransaksi, "/api/transaksi/add")

api.add_resource(GetFavoriteToken, "/api/pushtoken/all")
api.add_resource(GetAllPushToken, "/api/pushtoken")

