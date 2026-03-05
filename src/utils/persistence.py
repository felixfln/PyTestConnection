import json
import os
from .logger import logger

class PersistenceManager:
    def __init__(self, file_path="data/data.txt"):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        header_line = "Data|Hora|Download|Upload|Ping|Jitter|PerdaPacotes|Servidor|Interface|IP|RedesSociais|StreamingHD|VideoConf|Gaming|Streaming4K|DownloadsPesados|Nota\n"
        
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(header_line)
        else:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    first_line = f.readline()
                if not first_line.startswith("Data"):
                    logger.warning("Cabeçalho inválido detectado. Criando backup e reiniciando arquivo de dados.")
                    os.rename(self.file_path, self.file_path + f".{int(os.path.getmtime(self.file_path))}.bak")
                    with open(self.file_path, "w", encoding="utf-8") as f:
                        f.write(header_line)
            except Exception as e:
                logger.error(f"Erro ao verificar integridade do arquivo de dados: {e}")

    def save_record(self, record):
        fields = [
            str(record.get("date", "")),
            str(record.get("time", "")),
            f"{record.get('download', 0):.2f}",
            f"{record.get('upload', 0):.2f}",
            f"{record.get('ping', 0):.2f}",
            f"{record.get('jitter', 0):.2f}",
            f"{record.get('packet_loss', 0):.2f}",
            str(record.get("server", "")),
            str(record.get("interface", "")), # Garantir que interface seja salva
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

    def load_records(self):
        records = []
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
        
        def sort_key(r):
            try:
                d = r.get("Data", "01/01/2000").split("/")
                return (f"{d[2]}{d[1]}{d[0]}", r.get("Hora", "00:00:00"))
            except: return ("00000000", "00:00:00")

        records.sort(key=sort_key, reverse=True)
        return records
