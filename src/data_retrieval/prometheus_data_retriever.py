from .data_retriever import DataRetriever
import configparser
from datetime import timedelta
from prometheus_api_client.utils import parse_datetime
from prometheus_api_client import PrometheusConnect


class PrometheusDataRetriever(DataRetriever):

    def retrieve_data(self, points_info):
        config_obj = configparser.ConfigParser()
        config_obj.read("config.ini")
        prometheus_host = config_obj["prometheus"]['prometheus_host']
        prometheus_port = config_obj["prometheus"]['prometheus_port']
        prom = PrometheusConnect(
            url=prometheus_host+":"+prometheus_port, disable_ssl=True)

        dict_points = {}
        for point_info in points_info:
            dict_points[point_info['measurement_name']] = (
                point_info['measurement_query'], point_info['start_time'], point_info['end_time'], point_info['steps'], point_info['measurement_name'])

        dict_points_values = {}
        for item in dict_points.values():
            start_time = parse_datetime(item[1])
            end_time = parse_datetime(item[2])
            metric_data = prom.custom_query_range(
                item[0],
                start_time=start_time,
                end_time=end_time,
                step=item[3]
            )
            list_values = []
            dict_res = dict(metric_data[0])
            for item1 in dict_res['values']:
                list_values.append(item1[1])
            dict_points_values[item[4]] = list_values

        multi_dim_array = []
        for item in dict_points_values.values():
            multi_dim_array.append(item)

        return list(dict_points_values.keys()), multi_dim_array
