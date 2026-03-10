import time
import requests
from typing import Optional, Callable, Dict, Any
from .base import BaseEngine
from ..utils.network import measure_jitter

class CloudflareEngine(BaseEngine):
    def get_name(self) -> str:
        return "Cloudflare Edge"

    def measure(self, callback: Optional[Callable[[str, Any], None]] = None) -> Dict[str, Any]:
        """Implementação via Cloudflare Speed Test Endpoints (Muito Estável)."""
        try:
            if callback: callback("status", "Preparando motor Cloudflare Edge...")
            
            payload_size_mb = 15 # 15 Megabytes de teste
            payload_bytes = payload_size_mb * 1024 * 1024
            
            if callback: 
                callback("progress", 10)
                callback("status", "Medindo latência (Ping)...")
                
            # Ping para Cloudflare DNS / Edge
            ping_host = "1.1.1.1" # Proxy de servidor da cloudflare (Anycast super rapido)
            
            # Utilizar o requests para obter ping e headers
            r_ping = requests.get("https://speed.cloudflare.com/meta", timeout=5)
            meta = r_ping.json() if r_ping.status_code == 200 else {}
            
            client_ip = meta.get("clientIp", "Desconhecido")
            asn = meta.get("asn", "Desconhecido")
            as_org = meta.get("asOrganization", "ISP")
            server_colo = meta.get("colo", "Cloudflare")
            
            if callback:
                callback("server", f"Cloudflare {server_colo}")
                callback("interface", f"{as_org} (AS{asn})")
                callback("ip", client_ip)
                callback("progress", 20)

            # Usamos o requests elapsed time ou nosso Network measure tool (melhor o nosso)
            import subprocess
            import platform
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            
            try:
                # Tentar ping rapido real
                output = subprocess.check_output(['ping', param, '1', ping_host], stderr=subprocess.STDOUT, universal_newlines=True)
                if 'ms' in output:
                    import re
                    match = re.search(r'(?:tempo|time)[=<](\d+)', output)
                    ping = float(match.group(1)) if match else r_ping.elapsed.total_seconds() * 1000
                else:
                    ping = r_ping.elapsed.total_seconds() * 1000
            except:
                ping = r_ping.elapsed.total_seconds() * 1000 # fallback
                
            if callback:
                callback("ping", ping)
                callback("progress", 30)
                callback("status", "Medindo estabilidade e perda de pacotes...")
                
            from ..utils.network import measure_network_quality
            net_q = measure_network_quality(ping_host)
            jitter = net_q["jitter"]
            packets_lost = net_q["packets_lost"]
            packets_sent = net_q["packets_sent"]
            
            # Cálculo de porcentagem amigável
            loss_pct = (packets_lost / packets_sent) * 100 if packets_sent > 0 else 0
            packet_loss_str = f"{packets_lost}/{packets_sent} ({int(loss_pct)}%)"

            if callback:
                callback("jitter", jitter)
                callback("packet_loss", packet_loss_str)
                callback("progress", 40)
            
            if callback: callback("status", "Medindo velocidade de DOWNLOAD...")
            
            # Usando uma URL de arquivo estático pública para download de teste
            # Exemplo: um arquivo grande na rede Cloudflare (100MB do speed.cloudflare.com)
            t0 = time.time()
            try:
                # O endpoint __down requer bytes especificados e retorna dados binários puramente
                r_down = requests.get(f"https://speed.cloudflare.com/__down?bytes={payload_bytes}", timeout=20, stream=True)
                download_bytes_received = 0
                for chunk in r_down.iter_content(chunk_size=1024*1024):
                    if chunk:
                        download_bytes_received += len(chunk)
                download_time = time.time() - t0
                
                if download_bytes_received > 0 and download_time > 0:
                    download_mbps = (download_bytes_received * 8 / 1_000_000) / download_time
                else:
                    download_mbps = 0.0
            except:
                download_mbps = 0.0
                
            if callback:
                callback("download", download_mbps)
                callback("progress", 70)
                
            if callback: callback("status", "Medindo velocidade de UPLOAD...")
            upload_size_mb = 10
            upload_bytes = upload_size_mb * 1024 * 1024
            dummy_data = b'0' * upload_bytes
            
            t0 = time.time()
            try:
                r_up = requests.post("https://speed.cloudflare.com/__up", data=dummy_data, timeout=20)
                upload_time = time.time() - t0
                
                if r_up.status_code == 200 and upload_time > 0:
                    upload_mbps = (upload_size_mb * 8) / upload_time
                else:
                    upload_mbps = 0.0
            except:
                upload_mbps = 0.0

            if callback:
                callback("upload", upload_mbps)
                callback("progress", 90)

            return {
                "download": download_mbps,
                "upload": upload_mbps,
                "ping": ping,
                "jitter": jitter,
                "packet_loss": packet_loss_str,
                "packets_lost": packets_lost,
                "packets_sent": packets_sent,
                "server": f"Cloudflare {server_colo}",
                "server_host": ping_host,
                "ip": client_ip,
                "interface": as_org
            }
        except Exception as e:
            raise RuntimeError(f"CloudflareEngine falhou: {e}")
