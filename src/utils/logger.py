import logging
import os
from datetime import datetime

class AppLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppLogger, cls).__new__(cls)
            cls._instance._setup()
        return cls._instance
    
    def _setup(self):
        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Nome único por execução: app_AAAAMMDD_HHMMSS.log
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(self.log_dir, f"app_{timestamp}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("PyTestConnection")

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg, exc_info=True):
        self.logger.error(msg, exc_info=exc_info)

    def critical(self, msg, exc_info=True):
        self.logger.critical(msg, exc_info=exc_info)

logger = AppLogger()
