import logging
import os
from datetime import datetime
from typing import Optional, Any
from ..constants import LOG_DIR

class AppLogger:
    _instance: Optional['AppLogger'] = None
    logger: logging.Logger
    current_log_file: str = ""
    
    def __new__(cls) -> 'AppLogger':
        if cls._instance is None:
            cls._instance = super(AppLogger, cls).__new__(cls)
            cls._instance._setup()
        return cls._instance
    
    def _setup(self) -> None:
        log_dir = LOG_DIR
        os.makedirs(log_dir, exist_ok=True)
        
        # Nome único por execução: app_AAAAMMDD_HHMMSS.log
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.current_log_file = os.path.join(log_dir, f"app_{timestamp}.log")
        
        # Base Logger
        self.logger = logging.getLogger("PyTestConnection")
        self.logger.setLevel(logging.INFO)
        
        # Console Handler (Legível)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        
        # File Handler (Texto Puro)
        file_handler = logging.FileHandler(self.current_log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
 
    def info(self, msg: str) -> None:
        self.logger.info(msg)

    def warning(self, msg: str) -> None:
        self.logger.warning(msg)

    def error(self, msg: str, exc_info: bool = True) -> None:
        self.logger.error(msg, exc_info=exc_info)

    def critical(self, msg: str, exc_info: bool = True) -> None:
        self.logger.critical(msg, exc_info=exc_info)

logger = AppLogger()
