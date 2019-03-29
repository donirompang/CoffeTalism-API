import logging, json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from blueprints.client import Clients

from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims

bp_auth = Blueprint('auth', __name__)
api = Api(bp_auth)


class CreateTokenResources(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        args = parser.parse_args()

        qry = Clients.query.filter_by(username=args['username']).filter_by(password=args['password']).first()
        
        resp = {}
        resp['status'] = 404
        resp['results'] = {}
        if qry is not None:
            token = create_access_token(marshal(qry, Clients.response_field))
            tmp = {}
            tmp['token'] = token
            tmp['userId'] = qry.id
            tmp['mode'] = qry.mode
            resp['status'] = 200
            resp['results'] = tmp
        return resp, 200, { 'Content-Type': 'application/json' }


class RegisterClient(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        parser.add_argument('k_password', location='json', required=True)
        parser.add_argument('mode', location='json', required=True)
        parser.add_argument('lokasi', location='json', required=True)

        args = parser.parse_args()

        user_baru = Clients(None, args['username'], args['password'], args['mode'], args['lokasi'])
        db.session.add(user_baru)
        db.session.commit()

        resp = {}
        resp['status'] = 200
        resp['results'] = "Success register"
        return resp, 200, { 'Content-Type': 'application/json' }


api.add_resource(CreateTokenResources, '/api/login')
api.add_resource(RegisterClient, '/api/register')