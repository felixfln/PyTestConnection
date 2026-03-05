import speedtest
from .base import BaseEngine

class SpeedtestEngine(BaseEngine):
    def get_name(self):
        return "Speedtest.net"

    def measure(self, callback=None):
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            
            ping = st.results.ping
            if callback:
                callback("ping", ping)
            
            # Measuring Download
            download = st.download() / 1_000_000  # Convert to Mbps
            if callback:
                callback("download", download)
                
            # Measuring Upload
            upload = st.upload() / 1_000_000  # Convert to Mbps
            if callback:
                callback("upload", upload)
            
            results = st.results.dict()
            return {
                "download": download,
                "upload": upload,
                "ping": ping,
                "jitter": 0,  # speedtest-cli doesn't directly provide jitter
                "server": results["server"]["sponsor"],
                "ip": results["client"]["ip"],
                "interface": results["client"]["isp"]
            }
        except Exception as e:
            raise RuntimeError(f"SpeedtestEngine failed: {e}")
