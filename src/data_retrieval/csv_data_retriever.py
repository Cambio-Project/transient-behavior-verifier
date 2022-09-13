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

        if column_names[0] == 'Simulation Time':
            # remove the simulation time column since the row number represents the time unit
            column_names.pop(0)
            points_names.pop(0)

            # generate missing values for each time interval
            for item_index, item in enumerate(column_names):
                arr = []
                for sim_time_index, sim_time in enumerate(df['Simulation Time']):
                    if sim_time_index + 1 < len(df['Simulation Time']):
                        skipped_time = df['Simulation Time'][sim_time_index + 1] - df['Simulation Time'][sim_time_index]
                        j = 0
                        while j < skipped_time:
                            arr.append(df[item][sim_time_index])
                            j += 1
                    else:
                        arr.append(df[item][len(df[item])-1])
                multi_dim_array.append(arr)
        else:
            for item in column_names:
                multi_dim_array.append(df[item].tolist())

        return multi_dim_array, column_names, points_names
