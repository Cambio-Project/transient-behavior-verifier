import logging
import time
from audioop import mul
from typing import Tuple

import jsonschema
from jsonschema import validate
import json
from flask import Flask, make_response, request, jsonify, abort, render_template, Response, send_file, Blueprint
import numpy
from data_retrieval.csv_data_retriever import CSVDataRetriever
from data_retrieval.influx_data_retriever import InfluxDataRetriever
from data_retrieval.prometheus_data_retriever import PrometheusDataRetriever
from data_retrieval.misim_retriever import MisimDataRetriever
from handlers.specification import Specification
from mtl_evaluation.mtl_evaluator import MTLEvaluator
from mtl_evaluation.mtl_refinement import MTLTimeRefiner, MTLPredicateRefiner
import handlers.predicate_functions as predicate_functions
import pandas as pd
import configparser


logic_api = Blueprint('logic_api', __name__)


@logic_api.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


@logic_api.route('/refine_timebound', methods=['POST'])
def refine_timebound():
    """
    Refines the timebound of the transient behavior specification.

    :return: Lower and upper bounds of when the transient behavior specification is satisfied.
    """
    formula_info = _formula_info_from_request()
    points_names, multi_dim_array = _data_from_formula_info(formula_info)

    end_mode = formula_info.get('endMode', False)
    if end_mode:
        points_names, multi_dim_array = _apply_end_mode(points_names, multi_dim_array)

    reverse = False
    if 'future-mtl' in formula_info:
        for array in multi_dim_array:
            array.reverse()
        reverse = True

    refiner = MTLTimeRefiner(formula_info, points_names, multi_dim_array, reverse)
    result = refiner.refine_timebound()
    return json.dumps(result)


@logic_api.route('/refine_predicate', methods=['POST'])
def refine_predicate():
    """
    Refines the predicate specification.

    :return: The interval (min, max, step) and the result of the refined predicate.
    """
    predicate = request.args['predicate']
    metric = request.args['metric']
    formula_info = _formula_info_from_request()
    points_names, multi_dim_array = _data_from_formula_info(formula_info)

    end_mode = formula_info.get('endMode', False)
    if end_mode:
        points_names, multi_dim_array = _apply_end_mode(points_names, multi_dim_array)

    reverse = False
    if 'future-mtl' in formula_info:
        for array in multi_dim_array:
            array.reverse()
        reverse = True

    refiner = MTLPredicateRefiner(formula_info, points_names, multi_dim_array, reverse)
    interval, result = refiner.refine_predicate(predicate, metric)
    return json.dumps({"interval": interval, "result": result})


@logic_api.route('/monitor', methods=['POST'])
def monitor():
    formula_info = _formula_info_from_request()
    mtl_result = start_evaluation(formula_info=formula_info)
    return mtl_result


def _formula_info_from_request() -> dict:
    """
    Extracts the formula and parameters from the request.

    :return: The formula, the parameters, and the formula info.
    """
    if request.headers.get('Content-Type') == 'application/json':
        formula_info = request.get_json()
    else:
        formula_info = json.loads(request.form['formula_json'])
    check_json_schema(formula_info)
    return formula_info


def _data_from_formula_info(formula_info: dict):
    options: dict = formula_info.get('options', {})
    source = formula_info["measurement_source"]

    if source == "influx":
        points_names, multi_dim_array = InfluxDataRetriever().retrieve_data(
            formula_info["measurement_points"]
        )

    elif source == "prometheus":
        points_names, multi_dim_array = PrometheusDataRetriever().retrieve_data(
            formula_info["measurement_points"]
        )

    elif source == "csv":
        f = request.files['file']
        #df = pd.read_csv(f.stream, header=0, sep=',')
        df = pd.read_csv(f.stream, header=0, sep=',|;', engine='python',skipinitialspace=True)
        multi_dim_array, column_names, points_names = CSVDataRetriever().retrieve_data(
            df, formula_info["measurement_points"]
        )

    elif source == "remote-csv":
        if not formula_info["remote-csv-address"]:
            raise ValueError("Remote CSV address not provided")
        df = pd.read_csv(formula_info['remote-csv-address'],skipinitialspace=True)
        multi_dim_array, column_names, points_names = CSVDataRetriever().retrieve_data(
            df, formula_info['measurement_points']
        )

    elif source == "misim":
        if not formula_info["remote-misim-address"]:
            raise ValueError("Remote MiSim Directory address not provided")
        sim_path = formula_info["remote-misim-address"]
        store_combined_file = options.get("store_combined_misim_results", False)
        multi_dim_array, points_names = MisimDataRetriever().retrieve_data(
            sim_path,
            formula_info["measurement_points"],
            store_combined_file
        )
    else:
        raise ValueError("Invalid measurement source")
    return points_names, multi_dim_array


def start_evaluation(formula_info):
    points_names, multi_dim_array = _data_from_formula_info(formula_info)

    end_mode = formula_info.get('endMode', False)
    if end_mode:
        points_names, multi_dim_array = _apply_end_mode(points_names, multi_dim_array)


    # if the formula is in future-MTL the trace is reversed and the results also
    reverse = False
    if 'future-mtl' in formula_info:
        for array in multi_dim_array:
            array.reverse()
        reverse = True

    options: dict = formula_info.get('options', {})
    formula_handler = Specification(formula_info)
    mtl_eval_output, intervals = MTLEvaluator(formula_handler).evaluate(
        points_names,
        multi_dim_array,
        reverse=reverse,
        create_plots=options.get('create_plots', True),
    )

    if reverse:
        intervals = reverse_intervals(intervals)
        mtl_eval_output.reverse()
    
    if end_mode:
        mtl_eval_output[1] = mtl_eval_output[0]
        mtl_eval_output = mtl_eval_output[:1]
        intervals = trim_last_interval(intervals)
    
    result_dict = {
        'result': str(mtl_eval_output[0]),
        'intervals': intervals
    }

    if 'future-mtl' in formula_info:
        result_dict['reversed-results'] = "True"

    # Make CTK fail on purpose when probe in method:
    # if(str(mtl_eval_output[-1])=="False"):
    #     sleep(5)
    #
    return json.dumps(result_dict)

def _apply_end_mode(points_names, multi_dim_array):
    """
    Add an "end" marker to the trace when endMode is enabled.
    
    - Appends "end" to points_names
    - Appends 0 to the end of each row in multi_dim_array
    - Appends a copy of the last row with the last value changed to 1
    """
    points_names = list(points_names)
    multi_dim_array = [list(row) for row in multi_dim_array]
    
    points_names.append("end")
    
    # Add 0 to the end of each existing row
    for row in multi_dim_array:
        row.append(0)
    
    # Copy the last row and change the last value to 1
    last_row = multi_dim_array[-1].copy()
    last_row[-1] = 1
    multi_dim_array.append(last_row)
    
    return points_names, multi_dim_array

def check_json_schema(formula_info):
    with open('behavior_json_schema.json', 'r') as file:
        schema = json.load(file)
    try:
        validate(instance=formula_info, schema=schema)
    except jsonschema.exceptions.ValidationError:
        raise Exception(
            "JSON Body is invalid! Some fields are incorrect or missing!"
        )


@logic_api.route('/insert_spec_into_exp', methods=['POST'])
def insert_spec_into_exp():
    json_file = request.files['exp_json']
    myfile = json_file.read()
    behav_spec = json.loads(request.form["formula_json"])
    json_obj = json.loads(myfile)

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

    config_obj = configparser.ConfigParser()
    config_obj.read("config.ini")
    host_address = config_obj["main_api"]['api_host'] + \
        ':'+config_obj["main_api"]['api_port']
    provider_obj["url"] = host_address+"/monitor"

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
    for item in request.form:
        if("pred_name_" in item and item[-1].isnumeric()):
            list_predicate_numbers.append(item[-1])
    set_predicate_numbers = set(list_predicate_numbers)

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
        elif("measurement_column_" in item and item[-1].isnumeric()):
            list_measurement_infos_numbers.append(item[-1])
    set_measurement_infos_numbers = set(list_measurement_infos_numbers)
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
    elif(dict_spec["measurement_source"] == "csv"):
        dict_spec["measurement_points"] = []
        for measr_number in set_measurement_infos_numbers:
            measurement_to_add = {}
            measurement_to_add["measurement_name"] = request.form["measurement_name_"+measr_number]
            measurement_to_add["measurement_column"] = request.form["measurement_column_"+measr_number]
            dict_spec["measurement_points"].append(measurement_to_add)

    with open('outputs/specification.json', 'w') as fp:
        json.dump(dict_spec, fp, indent=4)

    return send_file('outputs/specification.json', as_attachment=True)


@logic_api.route('/result', methods=['GET', 'POST'])
def result_endpoint():
    output = json.loads(monitor())
    return render_template('result_page.html', result=output['result'], intervals=output['intervals'])

def trim_last_interval(intervals):
    if not intervals:
        return intervals
    start, end, *rest = intervals[-1]
    if start == end:
        # Case: End is single point
        result = intervals[:-1]
        start_prev, end_pre, *rest_pre = intervals[-1]
        if end_pre == start_prev-1:
            # remove previous
            result = result[:-1]
        else:
            # shorten previous
            result[-1] = (start_prev, end_pre-1, *rest_pre)
        result.append((start-1, end-1, *rest))
    else:
        # Case: End is interval, shorten interval
        result = intervals[:-1]
        result.append((start, end-1, *rest))
    return result

def reverse_intervals(intervals):
    if not intervals:
        return intervals
    
    # increase end time of last interval by 1 since last interval is exclusive. Usually, (5,6) means at point 5, but in last interval it is (6,6) for point 6. We unify this behavior here and change it back later.
    last_start, last_end, *rest = intervals[-1]
    last_end += 1
    intervals[-1] = (last_start, last_end, *rest)

    # using the increased by one end time compensates for the fact that end times are exclusive. 
    max_time = last_end

    reversed_intervals = []
    for start, end, *rest in reversed(intervals):
        new_start = max_time - end
        new_end = max_time - start
        reversed_intervals.append((new_start, new_end, *rest))

    last_start, last_end, *rest = reversed_intervals[-1]
    last_end -= 1
    reversed_intervals[-1] = (last_start, last_end, *rest)

    return reversed_intervals