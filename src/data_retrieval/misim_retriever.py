from pathlib import Path
from typing import List, Any
from functools import reduce
import pandas as pd

from .data_retriever import DataRetriever


class MisimDataRetriever(DataRetriever):
    """
    Data retriever for the MiSim simulation files.
    """

    @staticmethod
    def create_array(sim_path: str, column_names: List[str], store_combined_file: bool):
        """
        MiSim outputs multiple CSV files, each containing the
        measurements for a single metric. This method combines
        the measurements into a single multidimensional array.

        :param sim_path: The path to the simulation files.
        :param column_names: A list of the measurement columns.
        :param store_combined_file: A boolean indicating whether to store the
            combined simulation data.
        :return: A multidimensional array of the simulation data.
        """
        files = Path(sim_path).glob('[!_]*.csv')

        if not files:
            raise FileNotFoundError("No simulation files found.")

        # Import each dataset file individually; do not use SimulationColumn as index as there can be duplicate values
        df_list = [pd.read_csv(file, index_col=False) for file in files]

        # Remove duplicates in datasets to avoid multiple entries per time unit; keep last entry always
        for i in range(len(df_list)):
            df_list[i] = df_list[i].drop_duplicates(subset=['SimulationTime'], keep='last')
        
        # Merge all rows into one based on SimulationTime column
        df = reduce(lambda left, right: left.merge(right, on="SimulationTime", how='outer'), df_list)

        # Since some files may start (or end) not at the same simulation time, the rows can become unsorted
        df = df.sort_values(by='SimulationTime')

        # Fill up missing values
        df = df.fillna(method="ffill", axis=0)
        df = df.fillna(method="bfill", axis=0)
        
        # Store combined csv file
        if store_combined_file:
            df.to_csv(Path(sim_path) / "_combined.csv", index=False)

        df = df[column_names]
        return df.to_numpy().T.tolist()

    def retrieve_data(self, sim_path: str, points_info: List[Any], store_combined_file: bool):
        """
        Retrieve data from the simulation files.

        :param sim_path: The path to the simulation files.
        :param points_info: A list of dictionaries containing the measurement
            names corresponding measurement columns.
        :param store_combined_file: A boolean indicating whether to store the
            combined simulation data.
        :return: A tuple containing the multi-dimensional array of the simulation
            data and the names of the points.
        """
        column_names = [point_info['measurement_column'] for point_info in points_info]
        multi_dim_array = self.create_array(sim_path, column_names, store_combined_file)
        points_names = [point_info['measurement_name'] for point_info in points_info]
        return multi_dim_array, points_names
