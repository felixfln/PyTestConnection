import speedtest
import threading
import time
import psutil
from typing import Optional, Callable, Dict, Any
from .base import BaseEngine
from ..utils.logger import logger

class SpeedtestEngine(BaseEngine):
    def get_name(self) -> str:
        return "Speedtest.net"

    def _live_monitor(self, stop_event: threading.Event, callback: Optional[Callable[[str, float], None]], mode: str = "download") -> None:
        """Monitora o tráfego real da rede durante o teste para o gráfico."""
        try:
            # Captura inicial
            last_io = psutil.net_io_counters()
            last_time = time.time()
            
            while not stop_event.is_set():
                time.sleep(0.3) # Amostragem a cada 300ms
                now = time.time()
                io = psutil.net_io_counters()
                
                elapsed = now - last_time
                if elapsed <= 0: continue
                
                if mode == "download":
                    # Bytes recebidos (Convertendo para Mbps)
                    diff = io.bytes_recv - last_io.bytes_recv
                else:
                    # Bytes enviados (Convertendo para Mbps)
                    diff = io.bytes_sent - last_io.bytes_sent
                
                speed_mbps = (diff * 8) / (elapsed * 1_000_000)
                
                # Só envia se houver atividade relevante ou para manter a linha viva
                if callback and speed_mbps > 0.1:
                    callback(mode, speed_mbps)
                
                last_io = io
                last_time = now
        except Exception as e:
            logger.warning(f"Live monitor falhou silenciosamente: {e}")

    def measure(self, callback: Optional[Callable[[str, Any], None]] = None) -> Dict[str, Any]:
        try:
            logger.info("Inicializando cliente Speedtest.net (Ambiente Seguro)")
            if callback: callback("status", "Preparando motor Speedtest.net...")
            st = speedtest.Speedtest(secure=True)
            if callback: callback("progress", 30)
            
            logger.info("Buscando melhor servidor...")
            if callback: callback("status", "Localizando servidor de teste ideal...")
            st.get_best_server()
            if callback: callback("progress", 40)
            
            # Captura metadados
            results_init = st.results.dict()
            if callback:
                callback("interface", results_init["client"]["isp"])
                callback("ip", results_init["client"]["ip"])
                callback("server", results_init["server"]["sponsor"])
                callback("progress", 50)

            # Latência
            if callback: callback("status", "Medindo latência (Ping)...")
            ping = st.results.ping
            if callback:
                callback("ping", ping)
                callback("progress", 55)

            # Jitter (Calculado logo após o ping como solicitado)
            from ..utils.network import measure_jitter
            server_host = results_init["server"]["host"]
            if callback: callback("status", "Medindo estabilidade (Jitter)...")
            jitter = measure_jitter(server_host)
            if callback:
                callback("jitter", jitter)
                callback("progress", 65)
            
            # --- MEDIÇÃO DE DOWNLOAD COM MONITORAMENTO VIVO ---
            logger.info("Iniciando Medição de Download (Live Monitoring)...")
            if callback: callback("status", "Medindo velocidade de DOWNLOAD...")
            stop_dl = threading.Event()
            monitor_dl = threading.Thread(target=self._live_monitor, args=(stop_dl, callback, "download"))
            monitor_dl.start()
            
            try:
                raw_download = st.download() / 1_000_000
            finally:
                stop_dl.set()
                monitor_dl.join()

            if callback:
                callback("download", raw_download)
                callback("progress", 80)
                
            # --- MEDIÇÃO DE UPLOAD COM MONITORAMENTO VIVO ---
            logger.info("Iniciando Medição de Upload (Live Monitoring)...")
            if callback: callback("status", "Medindo velocidade de UPLOAD...")
            stop_ul = threading.Event()
            monitor_ul = threading.Thread(target=self._live_monitor, args=(stop_ul, callback, "upload"))
            monitor_ul.start()
            
            try:
                raw_upload = st.upload() / 1_000_000
            finally:
                stop_ul.set()
                monitor_ul.join()

            if callback:
                callback("upload", raw_upload)
                callback("progress", 95)
            
            results = st.results.dict()
            return {
                "download": raw_download,
                "upload": raw_upload,
                "ping": ping,
                "jitter": jitter,
                "server": results["server"]["sponsor"],
                "server_host": results["server"]["host"],
                "ip": results["client"]["ip"],
                "interface": results["client"]["isp"]
            }
        except Exception as e:
            logger.error(f"Erro crítico no SpeedtestEngine: {e}")
            raise RuntimeError(f"SpeedtestEngine falhou: {e}")
