import subprocess
import re
import platform
import time
from ..utils.logger import logger

class EngineManager:
    def __init__(self):
        self.engines = []
        
        # Defensive loading
        try:
            from .speedtest_provider import SpeedtestEngine
            self.engines.append(SpeedtestEngine())
        except Exception as e:
            logger.error(f"Erro ao carregar SpeedtestEngine: {e}")

        try:
            from .alternative_provider import PySpeedtestEngine
            self.engines.append(PySpeedtestEngine())
        except Exception as e:
            logger.error(f"Erro ao carregar PySpeedtestEngine: {e}")

    def run_measurement(self, callback=None):
        error_messages = []
        for engine in self.engines:
            try:
                engine_name = engine.get_name()
                logger.info(f"Tentando medição com {engine_name}...")
                results = engine.measure(callback)
                
                if callback: callback("progress", 90)
                
                # Realiza medição de jitter baseada no host do servidor
                host = results.get("server_host")
                if not host:
                    # Tenta extrair host da URL se existir (ex: http://servidor.com:8080/speedtest/upload.php)
                    server_url = results.get("server", "")
                    host_match = re.search(r"https?://([^:/]+)", server_url)
                    host = host_match.group(1) if host_match else "8.8.8.8"

                logger.info(f"Iniciando cálculo de jitter para o host: {host}")
                jitter = self._measure_jitter(host)
                results["jitter"] = jitter
                
                if callback: callback("progress", 100)
                logger.info(f"Medição concluída com sucesso via {engine_name}")
                return results
            except Exception as e:
                err_msg = f"{engine.get_name()}: {str(e)}"
                logger.error(err_msg)
                error_messages.append(err_msg)
                continue
        
        final_error = "Todos os motores de medição falharam:\n" + "\n".join(error_messages)
        logger.error(final_error)
        raise RuntimeError(final_error)

    def _measure_jitter(self, host):
        """Calcula jitter baseado em pings reais (Variação média entre latências sucessivas)"""
        latencies = []
        try:
            # Remove porta do host se houver (ex: host.com:8080 -> host.com)
            clean_host = host.split(":")[0]
            
            param = "-n" if platform.system().lower() == "windows" else "-c"
            # 8 pings para uma amostragem melhor sem demorar muito
            command = ["ping", param, "8", clean_host]
            
            # Executa ping ocultando janela no Windows
            flags = 0x08000000 if platform.system() == "Windows" else 0
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=flags)
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.warning(f"Comando ping retornou erro {process.returncode} para {clean_host}: {stderr}")
                return 0.0

            # Regex aprimorado para capturar latência em PT e EN
            # Windows: "tempo=15ms" ou "time=15ms" ou "tempo < 1ms"
            # Linux: "time=15.2 ms"
            matches = re.findall(r"(?:tempo|time)[=<]\s*(\d+\.?\d*)", stdout, re.IGNORECASE)
            latencies = [float(m) for m in matches]
            
            logger.info(f"Pings realizados para {clean_host}: {latencies}")

            if len(latencies) < 2:
                logger.warning(f"Poucos pacotes retornados para cálculo de jitter do host {clean_host}")
                return 0.0 # Retornar 0 em vez de 1 se falhar
                
            # Jitter = Média das diferenças absolutas entre pings consecutivos
            diffs = [abs(latencies[i] - latencies[i-1]) for i in range(1, len(latencies))]
            jitter = sum(diffs) / len(diffs)
            return round(jitter, 2)
            
        except Exception as e:
            logger.error(f"Exceção durante cálculo de jitter: {e}")
            return 0.0
