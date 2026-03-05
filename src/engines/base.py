import abc

class BaseEngine(abc.ABC):
    @abc.abstractmethod
    def measure(self, callback=None):
        """
        Performs the measurement.
        callback(type, value): optional function to report real-time data
        returns: dict with results (download, upload, ping, jitter, server, ip)
        """
        pass

    @abc.abstractmethod
    def get_name(self):
        pass
