import sys
import os
import tkinter as tk
import psutil

# Fix for PyInstaller --windowed mode where sys.stdout/stderr are None
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

from src.constants import LOCK_FILE, VERSION

def single_instance_guard():
    """Terminates previous instances and stores current PID."""
    current_pid = os.getpid()
    
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, 'r') as f:
                old_pid = int(f.read().strip())
                
            if psutil.pid_exists(old_pid):
                process = psutil.Process(old_pid)
                # Ensure it's actually our app (simple check)
                if "PyTestConnection" in process.name() or "python" in process.name():
                    process.terminate()
        except:
            pass

    with open(LOCK_FILE, 'w') as f:
        f.write(str(current_pid))

from src.utils.logger import logger
from src.ui.app import InternetQualityApp

def main():
    logger.info("Tentativa de inicialização da aplicação.")
    single_instance_guard()
    logger.info("Instância única garantida. Iniciando interface gráfica.")
    root = tk.Tk()
    app = InternetQualityApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
