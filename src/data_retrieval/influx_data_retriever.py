from influxdb import InfluxDBClient
from .data_retriever import DataRetriever
import configparser


class InfluxDataRetriever(DataRetriever):
    """ A class extending the abstract DataRetriever class and implementing the retrieval of InfluxDB data. """

    # retrieves the last RunID from the TimeBatchRuns database
    def get_last_runid_from_batch_runs(self):
        config_obj = configparser.ConfigParser()
        config_obj.read("config.ini")
        influxdb_host = config_obj["influxdb"]['influxdb_host']
        influxdb_port = config_obj["influxdb"]['influxdb_port']
        client = InfluxDBClient(host=influxdb_host, port=influxdb_port)
        client.switch_database('TimeBatchRuns')
        result = client.query(
            'SELECT * FROM "TimeBatchRuns"."autogen"."Run_StartStop"')
        points = result.get_points()
        last_id = None
        for item in points:
            last_id = item['RunID']

        return last_id

    # retrieves the last RunID from the AliveInstances database
    def get_last_runid_from_alive_instances(self):
        config_obj = configparser.ConfigParser()
        config_obj.read("config.ini")
        influxdb_host = config_obj["influxdb"]['influxdb_host']
        influxdb_port = config_obj["influxdb"]['influxdb_port']
        client = InfluxDBClient(host=influxdb_host, port=influxdb_port)
        client.create_database('AliveInstances')
        client.switch_database('AliveInstances')
        result = client.query(
            'SELECT max("RunID") FROM "AliveInstances"."autogen"."InstanceCounts"')
        if(len(result) == 0):
            last_id = 0
        else:
            points = result.get_points()
            last_id = None
            for item in points:
                last_id = item['max']
        return last_id

    def retrieve_data(self, points_info):
        config_obj = configparser.ConfigParser()
        config_obj.read("config.ini")
        influxdb_host = config_obj['influxdb']['influxdb_host']
        influxdb_port = config_obj['influxdb']['influxdb_port']
        client = InfluxDBClient(host=influxdb_host, port=influxdb_port)
        points_names = {}
        for item in points_info:
            points_names[item['measurement_name']] = item['measurement_query']
        points_data = {}
        for key, value in points_names.items():
            if("TimeBatchRuns" in value):
                last_id = self.get_last_runid_from_batch_runs()
                client.switch_database('TimeBatchRuns')
                result = client.query(
                    value + ' WHERE "RunID"=\'' + last_id+'\' ')
                points = result.get_points()
                data_points = []
                for item in points:
                    data_points.append(item[list(item)[-1]])
            elif("AliveInstances" in value):
                last_id = str(self.get_last_runid_from_alive_instances())
                client.switch_database('AliveInstances')
                result = client.query(value + ' WHERE "RunID"=' + last_id)
                points = result.get_points()
                data_points = []
                for item in points:
                    data_points.append(item[list(item)[-1]])

            points_data[key] = data_points

        data_multi_dim_array = []
        for item in points_data.values():
            data_multi_dim_array.append(item)

        # check that all hava same length
        # TODO : FIX THIS !!!!!!!!!!!!!
        length = len(data_multi_dim_array[0])
        for item in data_multi_dim_array:
            print(length, len(item))
            if len(item) != length:
                item.append(3)
                # raise Exception(
                #     "Data points do not have the same dimensions/lengths!")

        return list(points_names.keys()), data_multi_dim_array
