from pathlib import Path
from typing import List, Any
from functools import reduce
import pandas as pd

from src.data_retrieval.data_retriever import DataRetriever


class MisimDataRetriever(DataRetriever):

    @staticmethod
    def create_array(sim_path: str, column_names: List[str]):
        files = Path(sim_path).glob('*.csv')
        df_list = [pd.read_csv(file, index_col="SimulationTime") for file in files]
        df = reduce(lambda left, right: left.join(right, on="SimulationTime"), df_list)
        df = df[column_names]
        df = df.fillna(method="ffill", axis=0)
        return df.to_numpy().T.tolist()

    def retrieve_data(self, sim_path: str, points_info: List[Any]):
        column_names = [point_info['measurement_column'] for point_info in points_info]
        multi_dim_array = self.create_array(sim_path, column_names)
        points_names = [point_info['measurement_name'] for point_info in points_info]
        return multi_dim_array, points_names
