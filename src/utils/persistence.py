import json
import os
from typing import List, Dict, Any, Tuple
from .logger import logger
from ..constants import DATA_FILE

class PersistenceManager:
    def __init__(self, file_path: str = DATA_FILE) -> None:
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self) -> None:
        header_line = "Data|Hora|Download|Upload|Ping|Jitter|PerdaPacotes|Servidor|Interface|Conexão|IP|RedesSociais|StreamingHD|VideoConf|Gaming|Streaming4K|DownloadsPesados|Nota\n"
        
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(header_line)
        else:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                if not lines or not lines[0].startswith("Data"):
                    logger.warning("Arquivo corrompido ou sem cabeçalho. Criando backup.")
                    os.rename(self.file_path, self.file_path + f".{int(os.path.getmtime(self.file_path))}.bak")
                    with open(self.file_path, "w", encoding="utf-8") as f:
                        f.write(header_line)
                elif "Conexão" not in lines[0]:
                    logger.info("Migrando arquivo de dados para incluir coluna 'Conexão'...")
                    header_old = lines[0].strip().split("|")
                    idx_interface = header_old.index("Interface") if "Interface" in header_old else 8
                    
                    new_lines = [header_line]
                    for line in lines[1:]:
                        parts = line.strip().split("|")
                        if len(parts) == len(header_old):
                            parts.insert(idx_interface + 1, "--")
                            new_lines.append("|".join(parts) + "\n")
                        else:
                            new_lines.append(line)
                            
                    with open(self.file_path, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)
            except Exception as e:
                logger.error(f"Erro ao verificar integridade do arquivo de dados: {e}")

    def save_record(self, record: Dict[str, Any]) -> None:
        fields = [
            str(record.get("date", "")),
            str(record.get("time", "")),
            f"{record.get('download', 0):.2f}",
            f"{record.get('upload', 0):.2f}",
            f"{record.get('ping', 0):.2f}",
            f"{record.get('jitter', 0):.2f}",
            f"{record.get('packet_loss', 0):.2f}",
            str(record.get("server", "")),
            str(record.get("interface", "")),
            str(record.get("connection_type", "--")),
            str(record.get("ip", "")),
            str(record.get("social_media", 0)),
            str(record.get("hd_streaming", 0)),
            str(record.get("video_conference", 0)),
            str(record.get("gaming", 0)),
            str(record.get("4k_streaming", 0)),
            str(record.get("heavy_downloads", 0)),
            str(record.get("grade", 0))
        ]
        line = "|".join(fields) + "\n"
        try:
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception as e:
            logger.error(f"Erro ao salvar registro: {e}")

    def load_records(self) -> List[Dict[str, str]]:
        records: List[Dict[str, str]] = []
        if not os.path.exists(self.file_path):
            return records
            
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if not lines: return []
                header = [h.strip() for h in lines[0].strip().split("|")]
                for line in lines[1:]:
                    values = [v.strip() for v in line.strip().split("|")]
                    if len(values) == len(header):
                        records.append(dict(zip(header, values)))
        except Exception as e:
            logger.error(f"Erro ao carregar registros: {e}")
            return []
        
        def sort_key(r: Dict[str, str]) -> Tuple[str, str]:
            try:
                # Ordenar por Data (YYYYMMDD) e dps Hora
                d = r.get("Data", "01/01/2000").split("/")
                return (f"{d[2]}{d[1]}{d[0]}", r.get("Hora", "00:00:00"))
            except: return ("00000000", "00:00:00")

        records.sort(key=sort_key, reverse=True)
        return records
