import abc
from typing import Optional, Callable, Dict, Any

class BaseEngine(abc.ABC):
    @abc.abstractmethod
    def measure(self, callback: Optional[Callable[[str, Any], None]] = None) -> Dict[str, Any]:
        """
        Performs the measurement.
        callback(type, value): optional function to report real-time data
        returns: dict with results (download, upload, ping, jitter, server, ip)
        """
        pass

    @abc.abstractmethod
    def get_name(self) -> str:
        """Returns the provider name."""
        pass
