from flask import Flask, render_template, request, send_file, Blueprint

gui_api = Blueprint('gui_api', __name__)


@gui_api.route('/', methods=['GET'])
def root_dash():
    return render_template('index.html')


@gui_api.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


@gui_api.route('/create_spec_mtl', methods=['GET'])
def create_spec_mtl():
    return render_template('create_spec_mtl.html')


@gui_api.route('/create_spec_psp', methods=['GET'])
def create_spec_psp():
    return render_template('create_spec_psp.html')


@gui_api.route('/create_exp', methods=['GET'])
def create_exp():
    return render_template('create_exp.html')


@gui_api.route('/verify_behav', methods=['GET'])
def verify_behav():
    return render_template('verify_behav.html')


@gui_api.route('/spec_selector', methods=['GET'])
def spec_selector():
    return render_template('spec_selector.html')
