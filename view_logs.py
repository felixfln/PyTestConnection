import base64
import os
import sys
from datetime import datetime

def decode_log(file_path):
    if not os.path.exists(file_path):
        print(f"Erro: Arquivo {file_path} não encontrado.")
        return

    print(f"--- Lendo Log: {os.path.basename(file_path)} ---")
    print("-" * 50)
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try:
                    # Decodifica de Base64 para Texto
                    decoded = base64.b64decode(line.encode('utf-8')).decode('utf-8')
                    print(decoded)
                except Exception:
                    print(f"[Linha Corrompida]: {line[:30]}...")
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
    print("-" * 50)

def main():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        print("Pasta de logs não encontrada.")
        return

    # Se passar um arquivo via argumento, lê ele. Senão, pega o mais recente.
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        files = [os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.endswith(".plog")]
        if not files:
            print("Nenhum arquivo .plog encontrado.")
            return
        target = max(files, key=os.path.getmtime)

    decode_log(target)

if __name__ == "__main__":
    main()
