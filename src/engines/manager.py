from .speedtest_provider import SpeedtestEngine
from .alternative_provider import PySpeedtestEngine

class EngineManager:
    def __init__(self):
        self.engines = [
            SpeedtestEngine(),
            PySpeedtestEngine()
        ]

    def run_measurement(self, callback=None):
        error_messages = []
        for engine in self.engines:
            try:
                print(f"Attempting measurement with {engine.get_name()}...")
                return engine.measure(callback)
            except Exception as e:
                error_messages.append(f"{engine.get_name()}: {str(e)}")
                continue
        
        raise RuntimeError("All measurement engines failed:\n" + "\n".join(error_messages))
