import subprocess
import re
import platform
from typing import List
from .logger import logger

def measure_jitter(host: str) -> float:
    """Calcula jitter baseado em pings reais (Variação média entre latências sucessivas)"""
    latencies: List[float] = []
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
        matches = re.findall(r"(?:tempo|time)[=<]\s*(\d+\.?\d*)", stdout, re.IGNORECASE)
        latencies = [float(m) for m in matches]
        
        if len(latencies) < 2:
            return 0.0
            
        # Jitter = Média das diferenças absolutas entre pings consecutivos
        diffs = [abs(latencies[i] - latencies[i-1]) for i in range(1, len(latencies))]
        jitter = sum(diffs) / len(diffs)
        return float(int(jitter * 100) / 100.0)
        
    except Exception as e:
        logger.error(f"Exceção durante cálculo de jitter: {e}")
        return 0.0
