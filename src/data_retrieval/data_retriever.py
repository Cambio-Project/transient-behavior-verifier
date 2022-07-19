from abc import ABC, abstractmethod
from influxdb import InfluxDBClient


class DataRetriever(ABC):
    """An abstract class that defines the structure of a DataRetriever. """

    @abstractmethod
    def retrieve_data(self, points_info):
        pass
