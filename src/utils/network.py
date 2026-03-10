import subprocess
import re
import platform
from typing import List
from .logger import logger

def measure_network_quality(host: str) -> dict:
    """Calcula jitter e perda de pacotes baseada em 10 pings reais."""
    latencies: List[float] = []
    packets_sent = 10
    try:
        clean_host = host.split(":")[0]
        param = "-n" if platform.system().lower() == "windows" else "-c"
        # 10 pings para precisão conforme solicitado
        command = ["ping", param, str(packets_sent), clean_host]
        
        flags = 0x08000000 if platform.system() == "Windows" else 0
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=flags)
        stdout, stderr = process.communicate()
        
        # O número de pings respondidos é a contagem de latências encontradas
        matches = re.findall(r"(?:tempo|time)[=<]\s*(\d+\.?\d*)", stdout, re.IGNORECASE)
        latencies = [float(m) for m in matches]
        
        packets_lost = packets_sent - len(latencies)
        
        jitter = 0.0
        if len(latencies) >= 2:
            diffs = [abs(latencies[i] - latencies[i-1]) for i in range(1, len(latencies))]
            jitter = sum(diffs) / len(diffs)
            jitter = float(int(jitter * 100) / 100.0)

        return {
            "jitter": jitter,
            "packets_sent": packets_sent,
            "packets_lost": packets_lost
        }
        
    except Exception as e:
        logger.error(f"Exceção durante cálculo de qualidade de rede: {e}")
        return {"jitter": 0.0, "packets_sent": packets_sent, "packets_lost": packets_sent}
