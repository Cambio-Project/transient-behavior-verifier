import configparser
from time import sleep
from flask import Flask, make_response, request, jsonify, abort, render_template, Response, send_file
from monitors import mtl
from werkzeug.datastructures import ImmutableMultiDict
import pandas as pd
from jsonschema import validate
from data_retrieval.csv_data_retriever import CSVDataRetriever
from data_retrieval.influx_data_retriever import InfluxDataRetriever
from handlers.formula_handler import FormulaHandler
from mtl_evaluation.mtl_evaluator import MTLEvaluator
import handlers.predicate_functions as predicate_functions
from pprint import pprint
from influxdb import InfluxDBClient
from logic_endpoints import logic_api
from gui_endpoints import gui_api

ALLOWED_EXTENSIONS = {'csv'}
UPLOAD_FOLDER = '/uploads/csv-uploads'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.register_blueprint(gui_api)
app.register_blueprint(logic_api)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    config_obj = configparser.ConfigParser()
    config_obj.read("config.ini")
    host_address = config_obj["main_api"]['api_host']
    app.run(host=host_address, debug=False)
