import logging, json
from flask import Blueprint, render_template, abort, request
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from flask_jwt_extended import jwt_required, get_jwt_claims
from jinja2 import TemplateNotFound
from datetime import datetime
from . import *
from blueprints.barang import *
from blueprints.bill import *
from blueprints.cart_detail import *
from blueprints.cart import *
from blueprints.client import *

bp_client = Blueprint('client', __name__, template_folder='../templates',static_folder='../static')
api = Api(bp_client)

class AddToCart(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('barangId', location='json', type=int, required=True)
        parser.add_argument('qty', location='json', type=int, required=True)
        
        args = parser.parse_args()

         
        user_id = get_jwt_claims()['id']
        qry = Cart.query.filter_by(user_id = user_id).filter_by(checkout='tidak').first()

        cart_id = 0

        if qry is None:
            cart_baru = Cart(None, user_id, 0, 0, None, None, 'tidak')
            db.session.add(cart_baru)
            db.session.commit()
            cart_id = cart_baru.id
        else:
            cart_id = qry.id


        barang = Barang.query.get(args['barangId'])
        cart_detail = None
        if barang is not None:
            cart_detail = CartDetail(None, cart_id, args['barangId'], args['qty'], barang.harga, None, None, None)
        else:
            return {"message" : "ID Barang not found"}, 404, { 'Content-Type': 'application/json' }

        db.session.add(cart_detail)
        db.session.commit()

        qry = Cart.query.get(cart_id)
        qry.total_qty = qry.total_qty + args['qty']
        qry.total_price = qry.total_price + barang.harga * args['qty']
        db.session.commit()

        return {"message" : "SUCCESS"}, 200, { 'Content-Type': 'application/json' }



class CheckItemInCart(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('idBarang', location='json', type=int, required=True)
        parser.add_argument('userId', location='json', type=int, required=True)
        
        args = parser.parse_args()

        user_id = args['userId']

        qry_cart = Cart.query.filter_by(user_id = user_id).filter_by(checkout = 'tidak').first()

        resp = {}
        resp['status'] = 404
        resp['results'] = 'not found'
        if qry_cart:
            cart_detail = CartDetail.query.filter_by(cart_id = qry_cart.id).filter_by(barang_id = args['idBarang']).filter_by(deleted = 'tidak').first()
            if cart_detail:
                resp['status'] = 200
                resp['results'] = 'found'
        return resp, 200, { 'Content-Type': 'application/json' }





class DelCartItem(Resource):
    @jwt_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cartDetailId', location='json', type=int, required=True)
        
        args = parser.parse_args()

        cart_detail = CartDetail.query.filter_by(id = args['cartDetailId']).filter_by(deleted = 'tidak').first()
        
        if cart_detail is not None:
            qry_cart = Cart.query.get(cart_detail.cart_id)

            qry_cart.total_qty = qry_cart.total_qty - cart_detail.qty
            qry_cart.total_price = qry_cart.total_price - cart_detail.price * cart_detail.qty
            
            cart_detail.deleted = "ya"
            db.session.commit()
            return {"Message" : "Deleted"}, 200, { 'Content-Type': 'application/json' }
        return {"message" : "Not Found"}, 404, { 'Content-Type': 'application/json' }


### API BARU
class UpdateStatusCart(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cartId', location='json', type=int, required=True)
        
        args = parser.parse_args()

        cart = Cart.query.get(args['cartId'])
        
        if cart is not None:
            cart.checkout = "ya"
            db.session.commit()
            return {"message" : "Updated"}, 200, { 'Content-Type': 'application/json' }
        return {"message" : "CartID Not Found"}, 404, { 'Content-Type': 'application/json' }



### API BARU
class CheckCartChild(Resource):
    @jwt_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cartId', location='args', type=int, required=True)
        
        args = parser.parse_args()

        list_cart_item = CartDetail.query.filter_by(cart_id = args['cartId']).filter_by(deleted = 'tidak').all()
        
        resp = {}
        resp['status'] = 404
        resp['results'] = "not found"
        if len(list_cart_item) > 0:
            resp['status'] = 200
            resp['results'] = "found"
        return resp, 200, { 'Content-Type': 'application/json' }




class UpdateCartItem(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cartDetailId', location='json', type=int, required=True)
        parser.add_argument('qty', location='json', type=int, required=True)
        
        args = parser.parse_args()

        cart_detail = CartDetail.query.filter_by(id = args['cartDetailId']).filter_by(deleted = 'tidak').first()
        
        if cart_detail is not None:
            barang = Barang.query.get(cart_detail.barang_id)
            if barang is not None:
                cart_detail.qty = args['qty']
                cart_detail.price = barang.harga
                db.session.commit()
                return marshal(cart_detail,CartDetail.response_field), 200, { 'Content-Type': 'application/json' }
            else:
                return {"message" : "ID Barang Not Found"}, 404, { 'Content-Type': 'application/json' }
        return {"message" : "Cart Item Not Found"}, 404, { 'Content-Type': 'application/json' }


class GetCartByUserId(Resource):
    @jwt_required
    def get(self, id):
        qry = Cart.query.filter_by(user_id = id).filter_by(checkout = 'tidak').first()
        resp = {}
        resp['status'] = 404
        resp['results'] = {}
        total_harga = 0
        total_qty = 0
        if qry:
            list_cart_item = CartDetail.query.filter_by(cart_id = qry.id).filter_by(deleted = 'tidak').all()
            if list_cart_item is not None:
                for row in list_cart_item:
                    total_harga = total_harga + row.price * row.qty
                    total_qty = total_qty + row.qty
                qry.total_price = total_harga
                qry.total_qty = total_qty
                db.session.commit()
                resp['status'] = 200
                resp['results'] = marshal(qry, Cart.response_field)
        return resp, 200, { 'Content-Type': 'application/json' }  


class GetAllCartItemByUserId(Resource):
    @jwt_required
    def get(self, id):
        qry = Cart.query.filter_by(user_id = id).filter_by(checkout = 'tidak').first()
        resp = {}
        resp['status'] = 404
        resp['results'] = []
        if qry:
            cart_id = qry.id
            list_cart_item = []
            qry = CartDetail.query.filter_by(cart_id = cart_id).filter_by(deleted = 'tidak').all()
            if qry:
                for row in qry:
                    tmp_item = {}
                    tmp_item['id'] = row.id
                    tmp_item['qty'] = row.qty
                    tmp_item['price'] = row.price
                    barang = Barang.query.get(row.barang_id)
                    barang = marshal(barang, Barang.response_field)
                    tmp_item['detail_barang'] = barang
                    list_cart_item.append(tmp_item)
                resp['results'] = list_cart_item
                resp['status'] = 200
        return resp, 200, { 'Content-Type': 'application/json' }  



class GetAllCartItemByCartId(Resource):
    @jwt_required
    def get(self, cartId):
        list_cart_detail = CartDetail.query.filter_by(cart_id = cartId).filter_by(deleted = 'tidak').all()
        resp = {}
        resp['status'] = 404
        resp['results'] = []
        if list_cart_detail:
            list_cart_item = []
            for row in list_cart_detail:
                tmp = marshal(row, CartDetail.response_field)
                list_cart_item.append(tmp)
            resp['results'] = list_cart_item
            resp['status'] = 200
        return resp, 200, { 'Content-Type': 'application/json' } 



class GetPopularBarang(Resource):
    def get(self):
        qry = Barang.query.order_by(Barang.terjual.desc()).limit(12).all()
        list_barang = []
        resp = {}
        if qry:
            for row in qry:
                barang = marshal(row,Barang.response_field)
                list_barang.append(barang)
            resp['status'] = 200
            resp['results'] = list_barang
            return resp, 200, { 'Content-Type': 'application/json' }
        resp['status'] = 404
        resp['results'] = list_barang
        return resp, 404, { 'Content-Type': 'application/json' }



class GetLatestBarang(Resource):
    def get(self):
        qry = Barang.query.order_by(Barang.created_at.desc()).limit(12).all()
        list_barang = []
        resp = {}
        if qry:
            for row in qry:
                barang = marshal(row,Barang.response_field)
                list_barang.append(barang)
            resp['status'] = 200
            resp['results'] = list_barang
            return resp, 200, { 'Content-Type': 'application/json' }
        resp['status'] = 404
        resp['results'] = list_barang
        return resp, 404, { 'Content-Type': 'application/json' }



class GetDetailBarang(Resource):
    def get(self, idBarang):
        qry = Barang.query.get(idBarang)
        resp = {}
        resp['status'] = 404
        resp['results'] = {}
        if qry:
            lokasi = Clients.query.get(qry.post_by_id).lokasi
            barang = marshal(qry,Barang.response_field)
            barang['lokasi'] = lokasi
            resp['status'] = 200
            resp['results'] = barang
        return resp, 200, { 'Content-Type': 'application/json' }


class CariBarang(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('keyword', location='json', default=" ")
        parser.add_argument('harga_bawah', location='json', default=0)
        parser.add_argument('harga_atas', location='json', default=999999999)
        parser.add_argument('lokasi', location='json', type=list , default=[])

        args = parser.parse_args()

        list_user_id = []
        list_barang = []


        for x in args['lokasi']:
            qry = Clients.query.filter_by(lokasi = x).all()
            for row in qry:
                list_user_id.append(row.id)


        if(len(args['lokasi']) == 0):
            qry = Barang.query.filter(Barang.nama.like("%"+args['keyword']+"%"))
            qry = qry.filter(Barang.harga >= args['harga_bawah'])
            qry = qry.filter(Barang.harga <= args['harga_atas']).all()
            for row in qry:
                barang = marshal(row, Barang.response_field)
                list_barang.append(barang)
        else:
            for post_id in list_user_id:
                qry = Barang.query.filter(Barang.nama.like("%"+args['keyword']+"%"))
                qry = qry.filter(Barang.harga >= args['harga_bawah'])
                qry = qry.filter(Barang.harga <= args['harga_atas']) 
                qry = qry.filter_by(post_by_id = post_id).all()
                for row in qry:
                    barang = marshal(row,Barang.response_field)
                    list_barang.append(barang)
            

        resp = {}
        resp['status'] = 404
        resp['results'] = list_barang
        if len(list_barang) > 0:
            resp['status'] = 200
            resp['results'] = list_barang
            return resp, 200, { 'Content-Type': 'application/json' }
        
        return resp, 200, { 'Content-Type': 'application/json' }


class KategoriBarang(Resource):
    def get(self, kategori):
        parser = reqparse.RequestParser()
        parser.add_argument('harga_bawah', location='args', default=0)
        parser.add_argument('harga_atas', location='args', default=999999999)
        parser.add_argument('lokasi', location='args', type=list, default=[])

        args = parser.parse_args()

        list_user_id = []
        list_barang = []


        for x in args['lokasi']:
            qry = Clients.query.filter_by(lokasi = x).all()
            for row in qry:
                list_user_id.append(row.id)


        if(len(args['lokasi']) == 0):
            qry = Barang.query.filter_by(kategori=kategori)
            qry = qry.filter(Barang.harga >= args['harga_bawah'])
            qry = qry.filter(Barang.harga <= args['harga_atas']).all()
            for row in qry:
                barang = marshal(row, Barang.response_field)
                list_barang.append(barang) 
        else:
            for post_id in list_user_id:
                qry = Barang.query.filter_by(kategori=kategori)
                qry = qry.filter(Barang.harga >= args['harga_bawah'])
                qry = qry.filter(Barang.harga <= args['harga_atas']) 
                qry = qry.filter_by(post_by_id = post_id).all()
                for row in qry:
                    barang = marshal(row,Barang.response_field)
                    list_barang.append(barang)


        resp = {}
        if len(list_barang) > 0:
            resp['status'] = 200
            resp['results'] = list_barang
            return resp, 200, { 'Content-Type': 'application/json' }
        resp['status'] = 404
        resp['results'] = []
        return resp, 200, { 'Content-Type': 'application/json' }



class AddToBill(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cart_id', location='json', type=int, required=True)
        parser.add_argument('jenis_alamat', location='json',required=True)
        parser.add_argument('alamat', location='json',required=True)
        parser.add_argument('no_hp', location='json',required=True)
        parser.add_argument('metode_pembayaran', location='json',required=True)
        parser.add_argument('status_pembayaran', location='json',required=True)
        
        args = parser.parse_args()

        user_id = get_jwt_claims()['id']

        bill_baru = Bill(None, args['cart_id'], user_id, args['jenis_alamat'], args['alamat'], args['no_hp'], args['metode_pembayaran'], args['status_pembayaran'], None, None, None, None)

        db.session.add(bill_baru)
        db.session.commit()
       
        return {"message" : "SUCCESS"}, 200, { 'Content-Type': 'application/json' }


class GetBillByUserId(Resource):
    @jwt_required
    def get(self):

        user_id = get_jwt_claims()['id']

        qry = Bill.query.filter_by(user_id = user_id).filter_by(selesai = 'tidak').all()
        list_bill = []
        resp = {}
        resp['status'] = 404
        resp['results'] = []
        if qry is not None:
            for row in qry:
                cart = Cart.query.get(row.cart_id)
                bill = marshal(row, Bill.response_field)
                bill['total_tagihan'] = cart.total_price
                list_bill.append(bill)
            resp['status'] = 200
            resp['results'] = list_bill
        return resp, 200, { 'Content-Type': 'application/json' }


class GetBillById(Resource):
    @jwt_required
    def get(self, billId):

        qry = Bill.query.get(billId)
        if qry is not None:
            return marshal(qry, Bill.response_field), 200, { 'Content-Type': 'application/json' }
        return {"Message" : "Not found"}, 404, { 'Content-Type': 'application/json' }



class UpdateBillSelesai(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('billId', location='json', type=int, required=True)
        
        args = parser.parse_args()

        bill = Bill.query.get(args['billId'])
        
        if bill is not None:
            bill.selesai = 'ya'
            db.session.commit()
            return {"message" : "Sukses"}, 200, { 'Content-Type': 'application/json' }
        return {"message" : "Bill ID Not Found"}, 404, { 'Content-Type': 'application/json' }


class CartIdToBillId(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cartId', location='json', type=int, required=True)
        
        args = parser.parse_args()

        bill = Bill.query.filter_by(cart_id = args['cartId']).first()
        resp = {}
        if bill is not None:
            bill.selesai = 'ya'
            db.session.commit()
            return {"Message" : "Sukses"}, 200, { 'Content-Type': 'application/json' }
        return {"message" : "Bill ID Not Found"}, 404, { 'Content-Type': 'application/json' }


class UpdateBill(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cartDetailId', location='json', type=int, required=True)
        parser.add_argument('barangId', location='json', type=int, required=True)
        parser.add_argument('qty', location='json', type=int, required=True)
        
        args = parser.parse_args()

        cart_detail = CartDetail.query.filter_by(id = args['cartDetailId']).filter_by(deleted = 'tidak').first()
        
        if cart_detail is not None:
            barang = Barang.query.get(args['barangId'])
            if barang is not None:
                cart = Cart.query.get(cart_detail.cart_id)
                cart.total_price = cart.total_price - cart_detail.price * cart_detail.qty
                cart.total_qty = cart.total_qty - cart_detail.qty

                cart_detail.barang_id = args['barangId']
                cart_detail.qty = args['qty']
                cart_detail.price = barang.harga
                db.session.commit()
                return marshal(cart_detail,CartDetail.response_field), 200, { 'Content-Type': 'application/json' }
            else:
                return {"message" : "ID Barang Not Found"}, 404, { 'Content-Type': 'application/json' }
        return {"message" : "Cart Item Not Found"}, 404, { 'Content-Type': 'application/json' }




api.add_resource(AddToCart, "api/cart/tambah")
api.add_resource(DelCartItem, "api/cartitem/delete")
api.add_resource(UpdateCartItem, "api/cartitem/update")
api.add_resource(GetAllCartItemByUserId, "api/cartitem/<int:id>")
api.add_resource(GetAllCartItemByCartId, "api/cart/cartid/<int:cartId>")
api.add_resource(GetCartByUserId, "api/cart/<int:id>")
api.add_resource(CheckItemInCart, "api/cart/cekbarang")
api.add_resource(UpdateStatusCart, "api/cart/update")
api.add_resource(CheckCartChild, "api/cart/check")

api.add_resource(CartIdToBillId, "api/cart/bill")


api.add_resource(AddToBill, "api/bill/tambah")
api.add_resource(UpdateBillSelesai, "api/bill/update")
api.add_resource(GetBillByUserId, "api/bill")
api.add_resource(GetBillById, "api/bill/<int:billId>")


api.add_resource(GetPopularBarang, "api/barang/popular")
api.add_resource(GetLatestBarang, "api/barang/latest")
api.add_resource(GetDetailBarang, "api/barang/<int:idBarang>")
api.add_resource(CariBarang, "api/barang/cari")
api.add_resource(KategoriBarang, "api/barang/kategori/<kategori>")

    






