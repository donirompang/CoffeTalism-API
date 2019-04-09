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
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

jwt = JWTManager(app)

@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    return identity


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:very_strong_password@127.0.0.1:3306/livecode_api'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:alphatech@127.0.0.1:3306/api_last'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1:3306/livecode_api'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:alphatech@127.0.0.1:3306/restlast'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

db.create_all()


api = Api(app, catch_all_404s=True)

from blueprints.penjual.resources import bp_penjual
app.register_blueprint(bp_penjual, url_prefix="/penjual")

from blueprints.pembeli.resources import bp_pembeli
app.register_blueprint(bp_pembeli, url_prefix="/pembeli")

from blueprints.auth import bp_auth
app.register_blueprint(bp_auth, url_prefix="/auth")

