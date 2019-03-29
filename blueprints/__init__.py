from flask import Flask, request, render_template
from flask_restful import Resource, Api, reqparse
from time import strftime
import json, logging
from logging.handlers import RotatingFileHandler
from flask_jwt_extended import JWTManager

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from datetime import timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = 'aku'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

jwt = JWTManager(app)

@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    return identity


# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://doni:doni@172.31.31.238:3306/livecode_api'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:very_strong_password@127.0.0.1:3306/livecode_api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

db.create_all()


api = Api(app, catch_all_404s=True)

from blueprints.client.resources import bp_client
app.register_blueprint(bp_client, url_prefix="/")

from blueprints.pelapak.resources import bp_pelapak
app.register_blueprint(bp_pelapak, url_prefix="/pelapak")

from blueprints.admin.resources import bp_admin
app.register_blueprint(bp_admin, url_prefix="/admin")

from blueprints.auth import bp_auth
app.register_blueprint(bp_auth, url_prefix="/auth")

