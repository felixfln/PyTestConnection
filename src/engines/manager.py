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
        for engine in self.engines:
            try:
                engine_name = engine.get_name()
                if callback: callback("status", f"Preparando motores de medição ({engine_name})...")
                
                results = engine.measure(callback)
                results["connection_type"] = connection_type # Preserva o que detectamos no início
                
                if callback: 
                    callback("progress", 100)
                    callback("status", "Teste finalizado.")
                
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

