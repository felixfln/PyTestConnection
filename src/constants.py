import os
import sys

VERSION = "1.0.6"

from src.utils.resource_manager import get_resource_path

# Caminhos de Arquivos e Recursos
if getattr(sys, 'frozen', False):
    # Rodando como executável (.exe)
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Rodando como script (.py)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "logs")
DATA_FILE = os.path.join(DATA_DIR, "data.pconn")
METRICS_CONFIG = get_resource_path(os.path.join("config", "metrics_config.json"))

ICON_PATH = get_resource_path(os.path.join("src", "assets", "app_icon.ico"))
SCHEDULER_ICON_PATH = get_resource_path(os.path.join("src", "assets", "schedule_icon.ico"))
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
