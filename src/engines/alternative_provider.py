import pyspeedtest
from typing import Optional, Callable, Dict, Any
from .base import BaseEngine

class PySpeedtestEngine(BaseEngine):
    def get_name(self) -> str:
        return "PySpeedtest (Alternativo)"

    def measure(self, callback: Optional[Callable[[str, Any], None]] = None) -> Dict[str, Any]:
        """Implementação simplificada usando pyspeedtest do PyPI"""
        try:
            st = pyspeedtest.SpeedTest()
            
            if callback: callback("progress", 10)
            ping = st.ping()
            if callback:
                callback("ping", ping)
                callback("progress", 30)
            
            if callback: callback("download", 0)
            download = st.download() / 1_000_000
            if callback:
                callback("download", download)
                callback("progress", 70)
            
            if callback: callback("upload", 0)
            upload = st.upload() / 1_000_000
            if callback:
                callback("upload", upload)
                callback("progress", 90)
            
            return {
                "download": download,
                "upload": upload,
                "ping": ping,
                "jitter": 0,
                "server": st.host,
                "server_host": st.host,
                "ip": "Desconhecido",
                "interface": "Desconhecido"
            }
        except Exception as e:
            raise RuntimeError(f"PySpeedtestEngine falhou: {e}")
