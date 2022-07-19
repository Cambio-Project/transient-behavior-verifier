from influxdb import InfluxDBClient
from .data_retriever import DataRetriever


class CSVDataRetriever(DataRetriever):
    """A class extending the DataRetriever abstract class.
    The class implements the retrieval of measurement data from CSV files."""

    def retrieve_data(self, df, data_points):
        column_names = []
        points_names = []
        for item in data_points:
            column_names.append(item['measurement_column'])
            points_names.append(item['measurement_name'])
        multi_dim_array = []
        for item in column_names:
            multi_dim_array.append(df[item].tolist())
        return multi_dim_array, column_names, points_names
