import speedtest
from .base import BaseEngine
from ..utils.logger import logger

class SpeedtestEngine(BaseEngine):
    def get_name(self):
        return "Speedtest.net"

    def measure(self, callback=None):
        try:
            # secure=True ajuda a evitar erros 403 em algumas redes
            # timeout aumentado para 20s
            logger.info("Inicializando cliente Speedtest.net (secure=True)")
            st = speedtest.Speedtest(secure=True)
            
            if callback: callback("progress", 10)
            
            logger.info("Buscando melhor servidor...")
            st.get_best_server()
            if callback: callback("progress", 30)
            
            ping = st.results.ping
            logger.info(f"Ping Speedtest: {ping}ms")
            if callback:
                callback("ping", ping)
                callback("progress", 40)
            
            # Ponto inicial do gráfico
            if callback: callback("download", 0)
                
            logger.info("Medindo Download...")
            # threads=None usa o padrão da biblioteca
            download = st.download() / 1_000_000  # Mbps
            logger.info(f"Download: {download:.2f} Mbps")
            if callback:
                callback("download", download)
                callback("progress", 70)
                
            if callback: callback("upload", 0)

            logger.info("Medindo Upload...")
            upload = st.upload() / 1_000_000  # Mbps
            logger.info(f"Upload: {upload:.2f} Mbps")
            if callback:
                callback("upload", upload)
                callback("progress", 90)
            
            results = st.results.dict()
            return {
                "download": download,
                "upload": upload,
                "ping": ping,
                "jitter": 0, # Calculado no EngineManager
                "server": results["server"]["sponsor"],
                "server_host": results["server"]["host"],
                "ip": results["client"]["ip"],
                "interface": results["client"]["isp"]
            }
        except Exception as e:
            logger.error(f"Erro em SpeedtestEngine: {e}")
            raise RuntimeError(f"SpeedtestEngine falhou: {e}")
