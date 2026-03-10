import json
import os
import base64
from typing import List, Dict, Any, Tuple
from .logger import logger
from ..constants import DATA_FILE

class PersistenceManager:
    def __init__(self, file_path: str = DATA_FILE) -> None:
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self) -> None:
        # Caminho antigo para migração
        old_file = self.file_path.replace(".pconn", ".txt")
        
        # Se o novo arquivo não existe mas o antigo sim, migrar
        if not os.path.exists(self.file_path) and os.path.exists(old_file):
            logger.info("Migrando banco de dados antigo para novo formato obfuscado...")
            try:
                records = self._load_old_format(old_file)
                os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
                for r in records:
                    self.save_record(r)
                # Renomeia o antigo para backup de segurança
                os.rename(old_file, old_file + ".migrated.bak")
                logger.info("Migração concluída com sucesso.")
            except Exception as e:
                logger.error(f"Falha na migração automática: {e}")

        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            # Diferente do formato anterior, não precisamos de cabeçalho legível no topo
            with open(self.file_path, "w", encoding="utf-8") as f:
                pass

    def _load_old_format(self, path: str) -> List[Dict[str, Any]]:
        records = []
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines: return []
            header = [h.strip() for h in lines[0].strip().split("|")]
            # Mapeamento de nomes de colunas do header antigo para nomes internos
            map_cols = {
                "Data": "date", "Hora": "time", "Download": "download", "Upload": "upload",
                "Ping": "ping", "Jitter": "jitter", "PerdaPacotes": "packet_loss",
                "Servidor": "server", "Interface": "interface", "Conexão": "connection_type",
                "IP": "ip", "RedesSociais": "social_media", "StreamingHD": "hd_streaming",
                "VideoConf": "video_conference", "Gaming": "gaming", 
                "Streaming4K": "4k_streaming", "DownloadsPesados": "heavy_downloads", "Nota": "grade"
            }
            for line in lines[1:]:
                values = line.strip().split("|")
                if len(values) == len(header):
                    record = {}
                    for h, v in zip(header, values):
                        key = map_cols.get(h, h.lower())
                        # Tentar converter para float onde apropriado
                        try:
                            if key in ["download", "upload", "ping", "jitter", "grade", "social_media", "hd_streaming", "video_conference", "gaming", "4k_streaming", "heavy_downloads"]:
                                record[key] = float(v)
                            else:
                                record[key] = v
                        except: record[key] = v
                    records.append(record)
        return records

    def save_record(self, record: Dict[str, Any]) -> None:
        try:
            # Serializa para JSON e depois codifica em Base64 para ficar "não legível"
            json_str = json.dumps(record)
            b64_str = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(b64_str + "\n")
        except Exception as e:
            logger.error(f"Erro ao salvar registro obfuscado: {e}")

    def load_records(self) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        if not os.path.exists(self.file_path):
            return records
            
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    try:
                        # Decodifica Base64 e depois desserializa JSON
                        json_str = base64.b64decode(line.encode('utf-8')).decode('utf-8')
                        record = json.loads(json_str)
                        
                        # Padroniza nomes para o Treeview (CapCase para compatibilidade com app.py)
                        # O app.py espera "Data", "Hora", etc.
                        compat_record = {
                            "Data": record.get("date", "--"),
                            "Hora": record.get("time", "--"),
                            "Download": record.get("download", 0),
                            "Upload": record.get("upload", 0),
                            "Ping": record.get("ping", 0),
                            "Jitter": record.get("jitter", 0),
                            "PerdaPacotes": record.get("packet_loss", "--"),
                            "Interface": record.get("interface", "--"),
                            "Conexão": record.get("connection_type", "--"),
                            "Nota": record.get("grade", 0),
                            "IP": record.get("ip", "--"),
                            "Servidor": record.get("server", "--"),
                            "RedesSociais": record.get("social_media", 0),
                            "StreamingHD": record.get("hd_streaming", 0),
                            "VideoConf": record.get("video_conference", 0),
                            "Gaming": record.get("gaming", 0),
                            "Streaming4K": record.get("4k_streaming", 0),
                            "DownloadsPesados": record.get("heavy_downloads", 0)
                        }
                        records.append(compat_record)
                    except Exception as e:
                        logger.warning(f"Falha ao decodificar linha de dados: {e}")
        except Exception as e:
            logger.error(f"Erro ao carregar registros obfuscados: {e}")
            return []
        
        def sort_key(r: Dict[str, str]) -> Tuple[str, str]:
            try:
                # Ordenar por Data (YYYYMMDD) e dps Hora
                d = r.get("Data", "01/01/2000").split("/")
                return (f"{d[2]}{d[1]}{d[0]}", r.get("Hora", "00:00:00"))
            except: return ("00000000", "00:00:00")

        records.sort(key=sort_key, reverse=True)
        return records
