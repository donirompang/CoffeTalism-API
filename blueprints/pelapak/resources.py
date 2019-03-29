import logging, json
from flask import Blueprint,render_template
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_claims

from . import *
from blueprints.barang import *
from blueprints.cart_detail import *
from blueprints.cart import *
from blueprints.bill import *

bp_pelapak = Blueprint('pelapak', __name__)
api = Api(bp_pelapak)


class PelapakTambahResource(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('namaBarang', location='json', required=True)
        parser.add_argument('hargaBarang', location='json', type=int, required=True)
        parser.add_argument('kategoriBarang', location='json', required=True)
        parser.add_argument('stokBarang', type=int, location='json', required=True)
        parser.add_argument('fotoBarang', location='json', required=True)
        parser.add_argument('deskripsiBarang', location='json', required=True)
        
        args = parser.parse_args()

        post_by_id = get_jwt_claims()['id']
        terjual = 0
        barang = Barang(None, args['namaBarang'], args['hargaBarang'], args['kategoriBarang'], args['stokBarang'], args['fotoBarang'], args['deskripsiBarang'], terjual, None, None, post_by_id)

        db.session.add(barang)
        db.session.commit()

        return {"message" : "SUCCESS"}, 200, { 'Content-Type': 'application/json' }


class PelapakUpdateResource(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('idBarang', location='json', type=int, required=True)
        parser.add_argument('namaBarang', location='json', default=None)
        parser.add_argument('hargaBarang', location='json', type=int, default=None)
        parser.add_argument('kategoriBarang', location='json', default=None)
        parser.add_argument('stokBarang', type=int, location='json', default=None)
        parser.add_argument('fotoBarang', location='json', default=None)
        parser.add_argument('deskripsiBarang', location='json', default=None)
        
        args = parser.parse_args()

        qry = Barang.query.get(args['idBarang'])
        
        if qry:
            user_id = get_jwt_claims()['id']

            if qry.post_by_id != user_id:
                return {"Message" : "Not allowed"}, 400, { 'Content-Type': 'application/json' }

            if args['namaBarang'] is not None:
                qry.nama = args['namaBarang']
            
            if args['hargaBarang'] is not None:
                qry.harga = args['hargaBarang']

            if args['kategoriBarang'] is not None:
                qry.kategori = args['kategoriBarang']

            if args['stokBarang'] is not None:
                qry.stok = args['stokBarang']

            if args['fotoBarang'] is not None:
                qry.foto = args['fotoBarang']

            if args['deskripsiBarang'] is not None:
                qry.deskripsi = args['deskripsiBarang']

            qry.updated_at = datetime.utcnow       
            db.session.commit()


            list_cart_detail = CartDetail.query.filter_by(barang_id = args['idBarang']).filter_by(deleted = 'tidak').all()
            if list_cart_detail is not None:
                for row in list_cart_detail:
                    tmp_barang = Barang.query.get(row.barang_id)
                    row.price = tmp_barang.harga
                    db.session.commit()
            return {"Message" : "Barang updated"}, 200, { 'Content-Type': 'application/json' }
        return {"Message" : "ID barang not found"}, 404, { 'Content-Type': 'application/json' }


class PelapakDeleteResource(Resource):
    @jwt_required
    def delete(self, idBarang):
        qry = Barang.query.get(idBarang)
        if qry:
            user_id = get_jwt_claims()['id']
            if qry.post_by_id != user_id:
                return {"Message" : "Not allowed"}, 400, { 'Content-Type': 'application/json' }

            list_cart_detail = CartDetail.query.filter_by(barang_id = idBarang).all()
            if list_cart_detail is not None:
                for row in list_cart_detail:
                    row.deleted = 'ya'
                    db.session.commit()
            db.session.delete(qry)
            db.session.commit()
            return {"Message" : "Deleted"}, 200, { 'Content-Type': 'application/json' }
        return {"Message" : "ID Barang not found"}, 404, { 'Content-Type': 'application/json' }


class PelapakGetAll(Resource):
    @jwt_required
    def get(self):
        user_id = get_jwt_claims()['id']
        qry = Barang.query.filter_by(post_by_id = user_id)
        listBarang = []
        resp = {}
        resp['status'] = 404
        resp['results'] = []
        if qry:
            for row in qry:
                barang = marshal(row,Barang.response_field)
                listBarang.append(barang)
            resp['status'] = 200
            resp['results'] = listBarang
        return resp, 200, { 'Content-Type': 'application/json' }

class PelapakGetById(Resource):
    @jwt_required
    def get(self, idBarang):
        user_id = get_jwt_claims()['id']
        qry = Barang.query.filter_by(post_by_id = user_id).filter_by(id = idBarang).all()
        if qry:
            barang = marshal(qry,Barang.response_field)
            return barang, 200, { 'Content-Type': 'application/json' }
        return {"Message" : "ID Barang not found"}, 404, { 'Content-Type': 'application/json' }



class PelapakGetPesanan(Resource):
    @jwt_required
    def get(self):
        user_id = get_jwt_claims()['id']
        
        bill_cart_id = Bill.query.filter_by(status_pembayaran = 'Menunggu Konfirmasi Penjual').all()
        
        list_cart_id = []
        for row in bill_cart_id:
            list_cart_id.append(row.cart_id)


        list_cart_detail_id = []
        for x in list_cart_id:
            list_cart_detail = CartDetail.query.filter_by(cart_id = x).filter_by(confirmed = 'tidak').filter_by(deleted = 'tidak').all()
            for cd in list_cart_detail:
                tmp = marshal(cd, CartDetail.response_field)
                list_cart_detail_id.append(tmp)

        list_owned_item = []
        for x in list_cart_detail_id:
            barang = Barang.query.get(x['barang_id'])
            if user_id == barang.post_by_id:
                list_owned_item.append(x)
        resp = {}
        resp['status'] = 200
        resp['results'] = list_owned_item
        return resp, 200, { 'Content-Type': 'application/json' }


class PelapakGetBillByCartId(Resource):
    @jwt_required
    def get(self, cartId):
        qry = Bill.query.filter_by(cart_id = cartId).first()
        if qry:
            bill = marshal(qry, Bill.response_field)
            return bill, 200, { 'Content-Type': 'application/json' }
        return {"Message" : "ID Barang not found"}, 404, { 'Content-Type': 'application/json' }



class PelapakConfirmItem(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cartDetailId', location='json', type=int, required=True)
        
        args = parser.parse_args()

        qry = CartDetail.query.get(args['cartDetailId'])
        
        if qry:
            qry.confirmed = 'ya'       
            db.session.commit()

            barang = Barang.query.get(qry.barang_id)
            barang.terjual = barang.terjual + qry.qty

            db.session.commit()
            return {"Message" : "Barang updated"}, 200, { 'Content-Type': 'application/json' }
        return {"Message" : "ID barang not found"}, 404, { 'Content-Type': 'application/json' }





api.add_resource(PelapakTambahResource, "/api/barang/tambah")
api.add_resource(PelapakUpdateResource, "/api/barang/update")
api.add_resource(PelapakDeleteResource, "/api/barang/delete/<int:idBarang>")
api.add_resource(PelapakGetAll, "/api/barang")
api.add_resource(PelapakGetById, "/api/barang/<int:idBarang>")
api.add_resource(PelapakGetBillByCartId, "/api/bill/<int:cartId>")

api.add_resource(PelapakGetPesanan, "/api/barang/pesanan")
api.add_resource(PelapakConfirmItem, "/api/barang/pesanan/confirm")



# @bp_pelapak.route('/dashboard')
# @jwt_required
# def dashboard():
#     try:
#         list_barang = []
#         user_id = get_jwt_claims()['id']
#         qry = Barang.query.filter_by(post_by_id = user_id).all() 
#         if qry is not None:
#             for row in qry:
#                 list_barang.append(row)
#             return render_template('index.html' , list_barang = list_barang)
#         return render_template('index.html' , list_barang = [])

#     except TemplateNotFound:
#         abort(404)


# @bp_pelapak.route('/')
# # @jwt_required
# def index():
#     return render_template('pelapak/pelapak_dashboard.html')

# @bp_pelapak.route('/delete')
# # @jwt_required
# def delete():
#     return render_template('pelapak/pelapak_delete.html')

# @bp_pelapak.route('/tambah')
# # @jwt_required
# def tambah():
#     return render_template('pelapak/pelapak_tambah.html')

# @bp_pelapak.route('/update')
# # @jwt_required
# def update():
#     return render_template('pelapak/pelapak_update.html')