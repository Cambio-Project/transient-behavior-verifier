from abc import ABC, abstractmethod
from influxdb import InfluxDBClient


class DataRetriever(ABC):

    @abstractmethod
    def retrieve_data(self, points_info):
        pass
