import json
import os

class PersistenceManager:
    def __init__(self, file_path="data/data.txt"):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write("Date|Time|Download|Upload|Ping|Jitter|PacketLoss|Server|Interface|IP|SocialMedia|HDStreaming|VideoConf|Gaming|4K|HeavyDocs|Grade\n")

    def save_record(self, record):
        """record is a dict with all fields"""
        fields = [
            record.get("date", ""),
            record.get("time", ""),
            f"{record.get('download', 0):.2f}",
            f"{record.get('upload', 0):.2f}",
            f"{record.get('ping', 0):.2f}",
            f"{record.get('jitter', 0):.2f}",
            f"{record.get('packet_loss', 0):.2f}",
            record.get("server", ""),
            record.get("interface", ""),
            record.get("ip", ""),
            str(record.get("social_media", 0)),
            str(record.get("hd_streaming", 0)),
            str(record.get("video_conference", 0)),
            str(record.get("gaming", 0)),
            str(record.get("4k_streaming", 0)),
            str(record.get("heavy_downloads", 0)),
            str(record.get("grade", 0))
        ]
        line = "|".join(fields) + "\n"
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(line)

    def load_records(self):
        records = []
        if not os.path.exists(self.file_path):
            return records
            
        with open(self.file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if len(lines) <= 1:
                return []
            
            header = lines[0].strip().split("|")
            for line in lines[1:]:
                values = line.strip().split("|")
                if len(values) == len(header):
                    records.append(dict(zip(header, values)))
        
        # Sort by date and time descending (Simplistic sort)
        records.sort(key=lambda x: (x["Date"], x["Time"]), reverse=True)
        return records
