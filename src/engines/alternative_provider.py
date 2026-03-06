import pyspeedtest
from typing import Optional, Callable, Dict, Any
from .base import BaseEngine

class PySpeedtestEngine(BaseEngine):
    def get_name(self) -> str:
        return "PySpeedtest (Alternativo)"

    def measure(self, callback: Optional[Callable[[str, Any], None]] = None) -> Dict[str, Any]:
        """Implementação simplificada usando pyspeedtest do PyPI"""
        try:
            if callback: callback("status", "Preparando motor PySpeedtest...")
            st = pyspeedtest.SpeedTest()
            
            if callback: 
                callback("progress", 30)
                callback("status", "Localizando servidor secundário...")
                callback("server", st.host)
                callback("interface", "Automático")
                callback("ip", "Calculando...")
                callback("progress", 40)

            if callback: callback("status", "Medindo latência (Ping)...")
            ping = st.ping()
            if callback:
                callback("ping", ping)
                callback("progress", 50)
            
            if callback: callback("status", "Medindo velocidade de DOWNLOAD...")
            download = st.download() / 1_000_000
            if callback:
                callback("download", download)
                callback("progress", 75)
            
            if callback: callback("status", "Medindo velocidade de UPLOAD...")
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
