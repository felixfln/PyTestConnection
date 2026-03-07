import subprocess
import re
import platform
import time
import statistics
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
            logger.warning(f"Erro ao carregar SpeedtestEngine: {e}")

        try:
            from .cloudflare_provider import CloudflareEngine
            import requests # Quick health check
            requests.get("https://speed.cloudflare.com/meta", timeout=3)
            self.engines.append(CloudflareEngine())
        except Exception as e:
            logger.warning(f"Motor CloudflareEngine inativo e desabilitado.")

    def run_measurement(self, callback: Optional[Callable[[str, Any], None]] = None, deep_test: bool = False) -> Dict[str, Any]:
        if callback: 
            callback("status", "Iniciando avaliação sobre a qualidade da internet...")
            callback("progress", 5)
            
        # 1. Detecta tipo de conexão LOGO NO INÍCIO
        if callback: callback("status", "Obtendo informações sobre sua conexão...")
        connection_type = self._get_connection_type()
        if callback: 
            callback("connection_type", connection_type)
            callback("progress", 10)

        error_messages = []
        all_results = []

        total_engines = len(self.engines)
        
        if deep_test:
            base_iterations = 5 if total_engines == 1 else 3
        else:
            base_iterations = 1
            
        total_tests = total_engines * base_iterations
        tests_done = 0

        for engine_idx, engine in enumerate(self.engines):
            engine_name = engine.get_name()
            iterations = base_iterations

            for iter_idx in range(iterations):
                try:
                    if deep_test:
                        status_msg = f"Teste Profundo ({engine_name} - {iter_idx+1}/{iterations})..."
                    else:
                        status_msg = f"Preparando motores de medição ({engine_name})..."
                    
                    if callback: callback("status", status_msg)
                    
                    # Wrapper for callback to scale progress if we do multiple tests
                    def wrapped_cb(m_type: str, val: Any) -> None:
                        if callback:
                            if m_type == "progress":
                                # Scale progress: (tests_done * 100 + val) / total_tests
                                # So each test takes 1/total_tests of the overall progress
                                current_step_progress = val if isinstance(val, (int, float)) else 0
                                scaled_progress = int(((tests_done * 100) + current_step_progress) / total_tests)
                                callback("progress", scaled_progress)
                            elif m_type == "status":
                                # We might want to keep our status instead of engine's default, or prepend
                                if deep_test:
                                    callback("status", f"Teste Profundo ({engine_name} - {iter_idx+1}/{iterations}): {val}")
                                else:
                                    callback("status", val)
                            else:
                                callback(m_type, val)

                    results = engine.measure(wrapped_cb)
                    results["connection_type"] = connection_type # Preserva o que detectamos no início
                    all_results.append(results)

                    tests_done += 1

                    if not deep_test:
                        if callback: 
                            callback("progress", 100)
                            callback("status", "Teste finalizado.")
                        
                        logger.info(f"Medição rápida concluída com sucesso via {engine_name}")
                        return results
                        
                except Exception as e:
                    err_msg = f"{engine.get_name()} (teste {iter_idx+1}): {str(e)}"
                    logger.error(err_msg)
                    error_messages.append(err_msg)
                    tests_done += 1 # advance step even on error
                    continue

        if not all_results:
            final_error = "Todos os testes nos motores selecionados falharam:\n" + "\n".join(error_messages)
            logger.error(final_error)
            raise RuntimeError(final_error)

        if deep_test:
            # Agrega por mediana inteligente e tolerante a falhas parciais
            if callback: callback("status", "Calculando estatísticas finais do teste profundo aguardando tolerância a falhas...")
            
            def get_median(key: str) -> float:
                # Filtra os valores válidos: pega maiores que 0 para não jogar a mediana pra baixo em falhas parciais (0.0)
                vals = [r[key] for r in all_results if key in r and isinstance(r[key], (int, float)) and r[key] > 0]
                return statistics.median(vals) if vals else 0.0

            final_res = {
                "download": get_median("download"),
                "upload": get_median("upload"),
                "ping": get_median("ping"),
                "jitter": get_median("jitter"),
                "connection_type": connection_type,
                # Campos de String: Busca de forma coesa a primeira válida ignorando "--" provindos de exceções de provedores falhos
                "server": next((r["server"] for r in all_results if r.get("server") and r["server"] != "--"), "--"),
                "ip": next((r["ip"] for r in all_results if r.get("ip") and r["ip"] != "--"), "--"),
                "interface": next((r["interface"] for r in all_results if r.get("interface") and r["interface"] != "--"), "--")
            }
            if callback: 
                callback("progress", 100)
                callback("status", "Teste profundo finalizado.")
            return final_res
        
        return all_results[0]


    def _get_connection_type(self) -> str:
        """Tenta detectar o tipo de conexão ativa usando critérios precisos do Windows."""
        if platform.system() != "Windows":
            return "--"
            
        try:
            flags = 0x08000000 # CREATE_NO_WINDOW
            
            # 1. Identifica a interface ativa via PowerShell (Rota Padrão 0.0.0.0/0)
            stdout_active = ""
            try:
                # Comando PS para pegar o adaptador físico da rota principal
                ps_cmd = (
                    '$rt = Get-NetRoute -DestinationPrefix "0.0.0.0/0" | Sort-Object RouteMetric | Select-Object -First 1; '
                    'if($rt) { Get-NetAdapter -InterfaceIndex $rt.InterfaceIndex | '
                    'Select-Object Name, InterfaceDescription, MediaType, LinkSpeed | ConvertTo-Json }'
                )
                process = subprocess.Popen(["powershell", "-Command", ps_cmd], 
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                          text=True, creationflags=flags)
                stdout_active, _ = process.communicate()
            except: pass

            active_adapter = {}
            if stdout_active.strip():
                try:
                    import json
                    active_adapter = json.loads(stdout_active)
                    if isinstance(active_adapter, list): active_adapter = active_adapter[0]
                except: pass

            # 2. Se for Wi-Fi ou detectado como tal, detalhamos via netsh
            is_wifi = False
            if active_adapter:
                media = str(active_adapter.get("MediaType", "")).lower()
                name = str(active_adapter.get("Name", "")).lower()
                if "802.11" in media or "wi-fi" in name or "wireless" in name:
                    is_wifi = True

            if is_wifi:
                try:
                    process = subprocess.Popen(["netsh", "wlan", "show", "interfaces"], 
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                              text=True, creationflags=flags)
                    stdout_wlan, _ = process.communicate()
                    
                    band = ""
                    # 1. Detecção por Canal (Netsh)
                    chan_match = re.search(r"(?:Canal|Channel)\s*:\s*(\d+)", stdout_wlan)
                    if chan_match:
                        channel = int(chan_match.group(1))
                        if 1 <= channel <= 14: band = " 2.4GHz"
                        elif 32 <= channel <= 177: band = " 5GHz"
                        elif channel >= 180: band = " 6GHz"
                    
                    # 2. Detecção por PhysicalMediaType ou Radio Type (Fallback)
                    phys_media = str(active_adapter.get("PhysicalMediaType", "")).lower()
                    radio_match = re.search(r"(?:Radio type|Tipo de rádio)\s*:\s*([^\r\n]*)", stdout_wlan)
                    radio = radio_match.group(1).lower() if radio_match else phys_media
                    
                    if not band and radio:
                        if any(x in radio for x in ["802.11be", "6ghz"]): band = " 6GHz"
                        elif any(x in radio for x in ["802.11ax", "802.11ac", "5ghz"]): band = " 5GHz"
                        elif "802.11n" in radio: 
                            speed_val = str(active_adapter.get("LinkSpeed", "0")).lower()
                            try:
                                speed_num = float(speed_val.split()[0].replace(',', '.'))
                                if "gbps" in speed_val or speed_num > 300: band = " 5GHz"
                                else: band = " 2.4GHz"
                            except: band = " 2.4GHz"
                        elif any(x in radio for x in ["802.11g", "802.11b", "2.4ghz"]): band = " 2.4GHz"
                    
                    # 3. Fallback Final por Velocidade (Se nada acima funcionar)
                    if not band:
                        speed_val = str(active_adapter.get("LinkSpeed", "0")).lower()
                        try:
                            speed_num = float(speed_val.split()[0].replace(',', '.'))
                            if "gbps" in speed_val or speed_num >= 300: band = " 5GHz"
                            else: band = " 2.4GHz"
                        except: band = " 2.4GHz"

                    ssid_match = re.search(r"SSID\s*:\s*([^\r\n]*)", stdout_wlan)
                    ssid = ssid_match.group(1).strip().lower() if ssid_match else ""
                    desc = str(active_adapter.get("InterfaceDescription", "")).lower()
                    
                    mobile_hints = ["iphone", "android", "galaxy", "motorola", "hotspot", "móvel", "mobile", "tether", "roteado"]
                    if any(hint in ssid for hint in mobile_hints) or any(hint in desc for hint in mobile_hints):
                        prefix = "Wi-Fi (Smartphone)" if any(x in desc for x in ["apple", "android"]) or any(x in ssid for x in ["iphone", "android"]) else "Wi-Fi Móvel"
                        return f"{prefix}{band}"
                    
                    return f"Wi-Fi{band}"
                except:
                    return "Wi-Fi"

            # 3. Heurística para Ethernet e Outros
            if active_adapter:
                desc = str(active_adapter.get("InterfaceDescription", "")).lower()
                name = str(active_adapter.get("Name", "")).lower()
                media = str(active_adapter.get("MediaType", "")).lower()
                
                # Mobile tethering via USB (Remote NDIS)
                mobile_keywords = ["remote ndis", "cellular", "wwan", "tethering", "apple mobile", "samsung mobile"]
                if any(kw in desc or kw in name for kw in mobile_keywords):
                    return "Internet Móvel (USB/Modem)"
                
                # Ethernet/Cabo
                if "802.3" in media or "ethernet" in media or "lan" in desc or "cabo" in name:
                    speed = str(active_adapter.get("LinkSpeed", ""))
                    if "Gbps" in speed or "1000" in speed or "gigabit" in desc:
                        return "Cabo (Giga Ethernet)"
                    return "Cabo (Ethernet)"

                return name[:15] if name else "Conexão Ativa"

            return "--"
            
        except Exception as e:
            logger.debug(f"Erro ao detectar tipo de conexão: {e}")
            return "--"

