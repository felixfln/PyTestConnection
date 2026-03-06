import subprocess
import re
import platform
import time
from typing import Optional, Callable, Dict, Any, List
from .base import BaseEngine
from ..utils.logger import logger

class EngineManager:
    def __init__(self) -> None:
        self.engines: List[BaseEngine] = []
        
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

    def run_measurement(self, callback: Optional[Callable[[str, Any], None]] = None) -> Dict[str, Any]:
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
                
                # Detecta tipo de conexão
                results["connection_type"] = self._get_connection_type()
                
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

    def _get_connection_type(self) -> str:
        """Tenta detectar o tipo de conexão com detalhes (Wi-Fi 2.4/5GHz, Cabo, Mobile)"""
        if platform.system() != "Windows":
            return "--"
            
        try:
            flags = 0x08000000 # CREATE_NO_WINDOW
            
            # 1. Tenta obter detalhes do Wi-Fi via netsh (mais preciso para bandas)
            stdout_wlan = ""
            try:
                process = subprocess.Popen(["netsh", "wlan", "show", "interfaces"], 
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                          text=True, creationflags=flags)
                stdout_wlan, _ = process.communicate()
            except: pass

            # 2. Obtém detalhes de todos os adaptadores FÍSICOS ativos via PowerShell
            stdout_ps = ""
            try:
                # Pegamos todos os adaptadores físicos que estão Up para análise
                ps_cmd = 'Get-NetAdapter | Where-Object { $_.Status -eq "Up" -and $_.Virtual -eq $false } | Select-Object Name, InterfaceDescription, MediaType, PhysicalMediaType, NdisPhysicalMedium | ConvertTo-Json'
                process = subprocess.Popen(["powershell", "-Command", ps_cmd], 
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                          text=True, creationflags=flags)
                stdout_ps, _ = process.communicate()
            except: pass

            # Parse do JSON do PowerShell
            adapters = []
            if stdout_ps.strip():
                try:
                    import json
                    data = json.loads(stdout_ps)
                    adapters = data if isinstance(data, list) else [data]
                except: pass

            # Se não achou adaptadores físicos ativos, retorna desconhecido
            if not adapters and not stdout_wlan:
                return "--"

            # 3. Lógica de decisão (Prioriza o que tem mais chance de ser a conexão principal)
            
            # Verifica Wi-Fi primeiro (netsh)
            if "State" in stdout_wlan and ("connected" in stdout_wlan or "conectado" in stdout_wlan):
                band = ""
                # Detecção de Banda por Canal
                chan_match = re.search(r"(?:Canal|Channel)\s*:\s*(\d+)", stdout_wlan)
                if chan_match:
                    channel = int(channel_val := int(chan_match.group(1)))
                    if channel <= 14: band = " 2.4GHz"
                    elif 32 <= channel <= 177: band = " 5GHz"
                    elif channel >= 180: band = " 6GHz"
                
                # Detecção de Banda por Tipo de Rádio (Fallback)
                if not band:
                    radio_match = re.search(r"(?:Radio type|Tipo de rádio)\s*:\s*([^\r\n]*)", stdout_wlan)
                    if radio_match:
                        radio = radio_match.group(1).lower()
                        if "802.11be" in radio: band = " 6GHz"
                        elif "802.11ax" in radio or "802.11ac" in radio: band = " 5GHz"
                        elif "802.11n" in radio: band = " (2.4/5GHz)"
                        elif "802.11g" in radio or "802.11b" in radio: band = " 2.4GHz"

                # Tenta extrair o SSID para ver se é hotspot
                ssid = ""
                ssid_match = re.search(r"SSID\s*:\s*([^\r\n]*)", stdout_wlan)
                if ssid_match:
                    ssid = ssid_match.group(1).strip().lower()

                # Verifica se é Hotspot de Celular pelo nome da rede ou descrição do hardware
                desc_lower = stdout_wlan.lower()
                mobile_hints = ["iphone", "android", "galaxy", "motorola", "xiaomi", "redmi", "huawei", "hotspot", "móvel", "mobile"]
                if any(hint in ssid for hint in mobile_hints) or any(hint in desc_lower for hint in mobile_hints):
                    return f"Wi-Fi Móvel{band}"
                
                return f"Wi-Fi{band}"

            # Verifica outros adaptadores (Ethernet / Móvel USB)
            for adapter in adapters:
                desc = str(adapter.get("InterfaceDescription", "")).lower()
                name = str(adapter.get("Name", "")).lower()
                media_type = str(adapter.get("MediaType", "")).lower()
                
                # Detecção de Internet Móvel (USB Tethering ou Modem Interno)
                mobile_keywords = ["remote ndis", "cellular", "móvel", "wwan", "tethering", "apple mobile", "samsung mobile"]
                if any(kw in desc or kw in name for kw in mobile_keywords):
                    return "Internet Móvel (USB/Modem)"
                
                # Detecção de Cabo (Ethernet)
                if "802.3" in media_type or "ethernet" in media_type or "lan" in desc:
                    # Dica de Fibra/Cabo (Muito difícil via software, mas podemos sugerir se for GigaEthernet)
                    if "gigabit" in desc or "gbe" in desc or "1000" in desc:
                        return "Cabo (Giga Ethernet)"
                    return "Cabo (Ethernet)"

            return "Conexão Local" if adapters else "--"
            
        except Exception as e:
            # Tolerante a falhas: se algo der errado, apenas retorna o básico ou vazio
            logger.debug(f"Erro ao detectar tipo de conexão: {e}")
            return "--"

    def _measure_jitter(self, host: str) -> float:
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
            
            logger.info(f"Pings realizados para {clean_host}: {latencies}")

            if len(latencies) < 2:
                logger.warning(f"Poucos pacotes retornados para cálculo de jitter do host {clean_host}")
                return 0.0
                
            # Jitter = Média das diferenças absolutas entre pings consecutivos
            diffs = [abs(latencies[i] - latencies[i-1]) for i in range(1, len(latencies))]
            jitter = sum(diffs) / len(diffs)
            # Ensure result is a float rounded to 2 decimal places
            return float(int(jitter * 100) / 100.0)
            
        except Exception as e:
            logger.error(f"Exceção durante cálculo de jitter: {e}")
            return 0.0
