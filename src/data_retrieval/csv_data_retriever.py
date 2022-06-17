from influxdb import InfluxDBClient
from .data_retriever import DataRetriever


class CSVDataRetriever(DataRetriever):

    def retrieve_data(self, df, data_points):
        # prepare table data
        column_names = []
        points_names = []
        for item in data_points:
            column_names.append(item['measurement_column'])
            points_names.append(item['measurement_name'])
        # print(column_names)
        multi_dim_array = []
        for item in column_names:
            multi_dim_array.append(df[item].tolist())
        # print(multi_dim_array)
        return multi_dim_array, column_names, points_names
