import jsonschema
from jsonschema import validate
import json
from flask import Flask, make_response, request, jsonify, abort, render_template, Response, send_file, Blueprint
from data_retrieval.csv_data_retriever import CSVDataRetriever
from data_retrieval.influx_data_retriever import InfluxDataRetriever
from data_retrieval.prometheus_data_retriever import PrometheusDataRetriever
from handlers.formula_handler import FormulaHandler
from mtl_evaluation.mtl_evaluator import MTLEvaluator
import handlers.predicate_functions as predicate_functions
import pandas as pd

logic_api = Blueprint('logic_api', __name__)


@logic_api.route('/monitor', methods=['POST'])
def monitor():

    if(request.headers.get('Content-Type') == 'application/json'):
        formula_info = request.get_json()
    else:
        formula_info = json.loads(request.form['formula_json'])

    check_json_schema(formula_info)
    print("Received new transient behavior specification.")
    formula, params_string = FormulaHandler().handle_formula(
        formula_info)
    mtl_result = start_evaluation(
        formula, params_string, formula_info['measurement_points'], formula_info['measurement_source'], formula_info)
    return mtl_result


def start_evaluation(formula, params_string, points_info, measurement_source, formula_info):

    if(measurement_source == "influx"):
        points_names, multi_dim_array = InfluxDataRetriever().retrieve_data(points_info)
    elif(measurement_source == "prometheus"):
        points_names, multi_dim_array = PrometheusDataRetriever().retrieve_data(points_info)
    elif(measurement_source == "csv"):
        f = request.files['file']
        df = pd.read_csv(f.stream, header=0, sep=',')
        multi_dim_array, column_names, points_names = CSVDataRetriever().retrieve_data(df,
                                                                                       points_info)
    elif(measurement_source == "remote-csv"):
        if(formula_info["remote-csv-address"]):
            df = pd.read_csv(formula_info['remote-csv-address'])
            multi_dim_array, column_names, points_names = CSVDataRetriever().retrieve_data(df,
                                                                                           points_info)

    mtl_eval_output, intervals = MTLEvaluator().evaluate(
        formula, params_string, points_names, multi_dim_array)

    result_dict = {}
    result_dict['result'] = str(mtl_eval_output[-1])
    result_dict['intervals'] = intervals
    print("Evaluation result:", result_dict['result'])
    # Make CTK fail on purpose when probe in method:
    # if(str(mtl_eval_output[-1])=="False"):
    #     sleep(5)
    # print("intervals", intervals)
    return json.dumps(result_dict)


def check_json_schema(formula_info):
    schema = None
    with open('behavior_json_schema.json', 'r') as file:
        schema = json.load(file)
    try:
        validate(instance=formula_info, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        # print(err)
        raise Exception(
            "JSON Body is invalid! Some fields are incorrect or missing!")


@logic_api.route('/insert_spec_into_exp', methods=['POST'])
def insert_spec_into_exp():
    print(request.form, request.files)
    json_file = request.files['exp_json']
    myfile = json_file.read()
    behav_spec = json.loads(request.form["formula_json"])
    json_obj = json.loads(myfile)

    print(behav_spec, json_obj)

    trans_behav_probe = {}
    trans_behav_probe["name"] = "Transient Behavior Check"
    trans_behav_probe["type"] = "probe"

    tolerance_obj = {}
    tolerance_obj["type"] = "jsonpath"
    tolerance_obj["path"] = "$.result"
    tolerance_obj["target"] = "body"
    tolerance_obj["expect"] = ["True"]

    trans_behav_probe["tolerance"] = tolerance_obj

    provider_obj = {}
    provider_obj["type"] = "http"
    provider_obj["url"] = "http://localhost:5000/monitor"
    provider_obj["method"] = "POST"
    provider_obj["headers"] = {"Content-Type": "application/json"}
    provider_obj["arguments"] = behav_spec

    trans_behav_probe["provider"] = provider_obj

    json_obj["steady-state-hypothesis"]["probes"].append(trans_behav_probe)

    with open('outputs/experiment.json', 'w') as fp:
        json.dump(json_obj, fp, indent=4)

    return send_file('outputs/experiment.json', as_attachment=True)


@logic_api.route('/save_spec', methods=['POST'])
def save_spec():
    specification = request.form['mtl_formula']
    behav_description = request.form['mtl_description']
    list_predicate_numbers = []
    print(request.form)
    for item in request.form:
        if("pred_name_" in item and item[-1].isnumeric()):
            list_predicate_numbers.append(item[-1])
    set_predicate_numbers = set(list_predicate_numbers)
    print("pred numbers", set_predicate_numbers)

    dict_spec = {}
    dict_spec["behavior_description"] = behav_description
    dict_spec["specification"] = specification
    dict_spec["specification_type"] = request.form['specification_type']
    dict_spec["predicates_info"] = []

    for pred_number in set_predicate_numbers:
        predicate_to_add = {}
        predicate_to_add["predicate_name"] = request.form["pred_name_"+pred_number]
        predicate_to_add["predicate_description"] = request.form["pred_description_"+pred_number]
        if("comp_value_"+pred_number in request.form):
            predicate_to_add["predicate_comparison_value"] = request.form["comp_value_"+pred_number]
        predicate_to_add["predicate_logic"] = request.form["pred_type_"+pred_number]
        dict_spec["predicates_info"].append(predicate_to_add)

    list_measurement_infos_numbers = []
    for item in request.form:
        if("measurement_query_" in item and item[-1].isnumeric()):
            list_measurement_infos_numbers.append(item[-1])
    set_measurement_infos_numbers = set(list_measurement_infos_numbers)
    print("measurement numbers", set_measurement_infos_numbers)
    dict_spec["measurement_source"] = request.form["measurement_select"]
    if(dict_spec["measurement_source"] == "influx"):
        dict_spec["measurement_points"] = []
        for measr_number in set_measurement_infos_numbers:
            measurement_to_add = {}
            measurement_to_add["measurement_name"] = request.form["measurement_name_"+measr_number]
            measurement_to_add["measurement_query"] = request.form["measurement_query_"+measr_number]
            dict_spec["measurement_points"].append(measurement_to_add)
    elif(dict_spec["measurement_source"] == "prometheus"):
        dict_spec["measurement_points"] = []
        for measr_number in set_measurement_infos_numbers:
            measurement_to_add = {}
            measurement_to_add["measurement_name"] = request.form["measurement_name_"+measr_number]
            measurement_to_add["measurement_query"] = request.form["measurement_query_"+measr_number]
            measurement_to_add["start_time"] = request.form["start_time_"+measr_number]
            measurement_to_add["end_time"] = request.form["end_time_"+measr_number]
            measurement_to_add["steps"] = request.form["steps_"+measr_number]
            dict_spec["measurement_points"].append(measurement_to_add)

    print(json.dumps(dict_spec))

    with open('outputs/specification.json', 'w') as fp:
        json.dump(dict_spec, fp, indent=4)

    return send_file('outputs/specification.json', as_attachment=True)


@logic_api.route('/result', methods=['GET', 'POST'])
def result_endpoint():
    output = json.loads(monitor())
    # print(output)
    # print("output intervals", output['intervals'])
    return render_template('result_page.html', result=output['result'], intervals=output['intervals'])
