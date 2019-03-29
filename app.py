# app.py
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from blueprints import app, manager
from time import strftime
import json, logging, sys
from logging.handlers import RotatingFileHandler

if __name__ == '__main__':
    ## define log format and create a rotating log with max size of 10MB and max backup up to 10 files
    # formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    # log_handler = RotatingFileHandler("%s/%s" % (app.root_path, '../storage/log/app.log'), maxBytes=10000, backupCount=10)
    # log_handler.setLevel(logging.INFO)
    # log_handler.setFormatter(formatter)
    # app.logger.addHandler(log_handler)
    logging.getLogger('flask_cors').level = logging.DEBUG

    try:
        if sys.argv[1] == 'db':
            manager.run()
        else:
            app.run(debug=False, host='0.0.0.0', port=5000)
    except Exception as e:
        app.run(debug=True, host='0.0.0.0', port=5000)


    
    
