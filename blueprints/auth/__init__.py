import logging, json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from blueprints.pembeli import Pembeli
from blueprints.penjual import Penjual
import re


from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims

bp_auth = Blueprint('auth', __name__)
api = Api(bp_auth)


def cekPattern(pattern, raw_string):
    w1 = re.search(pattern,raw_string)
    v1 = ''
    if(w1):
        v1 = w1.group()
        return(v1)
    return None


class LoginPembeli(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        args = parser.parse_args()

        qry = Pembeli.query.filter_by(username=args['username']).filter_by(password=args['password']).first()
        
        resp = {}
        resp['status'] = 404
        resp['results'] = {}
        if qry is not None:
            token = create_access_token(marshal(qry, Pembeli.response_field))
            tmp = {}
            tmp['token'] = token
            
            resp['status'] = 200
            resp['results'] = tmp
        return resp, 200, { 'Content-Type': 'application/json' }


class RegisterPembeli(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', location='json', required=True)
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        parser.add_argument('k_password', location='json', required=True)
        parser.add_argument('email', location='json', required=True)
        parser.add_argument('profilePicture', location='json')

        args = parser.parse_args()

        pattern_email = '^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$'
        email = cekPattern(pattern_email, args['email'])
        
        pattern_password = '^(?=.*[0-9]+.*)(?=.*[a-zA-Z]+.*)[0-9a-zA-Z]{6,}$'
        password = cekPattern(pattern_password, args['password'])
        
        resp = {}
        resp['status'] = 200
        resp['results'] = "Success register"

        qry = Pembeli.query.filter_by(username = args['username']).first()
        if qry is not None:
            resp['results'] = "Username already exist"
            return resp, 200, { 'Content-Type': 'application/json' }

        qry = Pembeli.query.filter_by(email = args['email']).first()
        if qry is not None:
            resp['results'] = "Email already exist"
            return resp, 200, { 'Content-Type': 'application/json' }



        if(not email):
            resp['results'] = "Email invalid"
            return resp, 200, { 'Content-Type': 'application/json' }

        if(not password):
            resp['results'] = "Password must containt atleast 1 number, 1 alphabhet and 6 characters"
            return resp, 200, { 'Content-Type': 'application/json' }


        if(args['password'] != args['k_password']):
            resp['results'] = "Password not match"
            return resp, 200, { 'Content-Type': 'application/json' }


        pembeliBaru = Pembeli(None, args['username'], args['name'], args['password'], args['email'], 0, None, args['profilePicture'], None, None)
        
        

        
        db.session.add(pembeliBaru)
        db.session.commit()

        return resp, 200, { 'Content-Type': 'application/json' }


class LoginPenjual(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        args = parser.parse_args()

        qry = Penjual.query.filter_by(username=args['username']).filter_by(password=args['password']).first()
        
        resp = {}
        resp['status'] = 404
        resp['results'] = {}
        if qry is not None:
            token = create_access_token(marshal(qry, Pembeli.response_field))
            tmp = {}
            tmp['token'] = token
            
            resp['status'] = 200
            resp['results'] = tmp
        return resp, 200, { 'Content-Type': 'application/json' }



class RegisterPenjual(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', location='json', required=True)
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        parser.add_argument('k_password', location='json', required=True)
        parser.add_argument('email', location='json', required=True)
<<<<<<< HEAD
        parser.add_argument('photo', location='json', required=True)
        parser.add_argument('alamat', location='json', required=True)
=======
        parser.add_argument('photo', location='json')
>>>>>>> 2bc4e7988f10a1f220a3b2ca6e6db668dacf58e8

        args = parser.parse_args()

        resp = {}
        resp['status'] = 200
        resp['results'] = "Success register"

        pattern_email = '^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$'
        email = cekPattern(pattern_email, args['email'])
        
        pattern_password = '^(?=.*[0-9]+.*)(?=.*[a-zA-Z]+.*)[0-9a-zA-Z]{6,}$'
        password = cekPattern(pattern_password, args['password'])

        qry = Penjual.query.filter_by(username = args['username']).first()
        if qry is not None:
            resp['results'] = "Username already exist"
            return resp, 200, { 'Content-Type': 'application/json' }

        qry = Penjual.query.filter_by(email = args['email']).first()
        if qry is not None:
            resp['results'] = "Email already exist"
            return resp, 200, { 'Content-Type': 'application/json' }


        if(not email):
            resp['results'] = "Email invalid"
            return resp, 200, { 'Content-Type': 'application/json' }

        if(not password):
            resp['results'] = "Password must containt atleast 1 number, 1 alphabhet and 6 characters"
            return resp, 200, { 'Content-Type': 'application/json' }


        if(args['password'] != args['k_password']):
            resp['results'] = "Password not match"
            return resp, 200, { 'Content-Type': 'application/json' }

        if(args['password'] != args['k_password']):
            resp['results'] = "Password not match"
            return resp, 200, { 'Content-Type': 'application/json' }

        penjualBaru = Penjual(None, args['username'], args['password'], args['name'], args['email'], None, args['photo'], None, args['alamat'], None)
        db.session.add(penjualBaru)
        db.session.commit()

        return resp, 200, { 'Content-Type': 'application/json' }



api.add_resource(LoginPembeli, '/api/pembeli/login')
api.add_resource(RegisterPembeli, '/api/pembeli/register')

api.add_resource(LoginPenjual, '/api/penjual/login')
api.add_resource(RegisterPenjual, '/api/penjual/register')