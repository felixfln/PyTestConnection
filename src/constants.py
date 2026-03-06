import os
import sys

VERSION = "1.0.0"

# Caminhos de Arquivos
DATA_FILE = "data/data.txt"
METRICS_CONFIG = "config/metrics_config.json"
LOG_DIR = "logs"
LOCK_FILE = os.path.join(os.getenv('TEMP', '.'), 'pytestconnection.lock')

# Paleta de Cores Premium (Sincronizada com app.py)
COLORS = {
    "bg": "#0f172a",
    "card": "#1e293b",
    "accent": "#22d3ee",
    "accent_dim": "#0891b2",
    "ul": "#fbbf24",       # Âmbar
    "amber": "#fbbf24",
    "text": "#f8fafc",
    "text_dim": "#94a3b8",
    "success": "#4ade80",
    "error": "#f43f5e",
    "border": "#334155"
}

# Configurações de UI
WINDOW_SIZE = "1100x950"
APP_TITLE = f"PyTestConnection v{VERSION}"

# Mapeamento do Semáforo (0=Red, 1=Yellow/Amber, 2=Green)
SEMAPHORE_COLORS = {
    0: COLORS["error"],
    1: COLORS["amber"],
    2: COLORS["success"]
}
