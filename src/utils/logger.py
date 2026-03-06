import logging
import os
from datetime import datetime
from typing import Optional, Any
from ..constants import LOG_DIR

class AppLogger:
    _instance: Optional['AppLogger'] = None
    logger: logging.Logger
    
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
        log_file = os.path.join(log_dir, f"app_{timestamp}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("PyTestConnection")
 
    def info(self, msg: str) -> None:
        self.logger.info(msg)

    def warning(self, msg: str) -> None:
        self.logger.warning(msg)

    def error(self, msg: str, exc_info: bool = True) -> None:
        self.logger.error(msg, exc_info=exc_info)

    def critical(self, msg: str, exc_info: bool = True) -> None:
        self.logger.critical(msg, exc_info=exc_info)

logger = AppLogger()
