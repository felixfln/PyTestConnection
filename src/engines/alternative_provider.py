import pyspeedtest
from .base import BaseEngine

class PySpeedtestEngine(BaseEngine):
    def get_name(self):
        return "PySpeedtest (Alternative)"

    def measure(self, callback=None):
        try:
            st = pyspeedtest.SpeedTest()
            
            ping = st.ping()
            if callback:
                callback("ping", ping)
            
            download = st.download() / 1_000_000
            if callback:
                callback("download", download)
            
            upload = st.upload() / 1_000_000
            if callback:
                callback("upload", upload)
            
            return {
                "download": download,
                "upload": upload,
                "ping": ping,
                "jitter": 0,
                "server": st.host,
                "ip": "Unknown",
                "interface": "Unknown"
            }
        except Exception as e:
            raise RuntimeError(f"PySpeedtestEngine failed: {e}")
