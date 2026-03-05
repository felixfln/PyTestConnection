import json
import os
import sys

class QualityCalculator:
    def __init__(self, config_path="config/metrics_config.json"):
        self.config = self._load_config(config_path)

    def _get_resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        path = os.path.join(base_path, relative_path)
        if not os.path.exists(path):
            # Fallback for dev environment structure
            path = os.path.join(os.path.dirname(__file__), "..", "..", relative_path)
        return path

    def _load_config(self, path):
        abs_path = self._get_resource_path(path)
        if os.path.exists(abs_path):
            with open(abs_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"metrics": {}, "scenarios": {}}

    def calculate_score(self, results):
        metrics_config = self.config.get("metrics", {})
        scores = []
        
        for key, metric in metrics_config.items():
            value = results.get(key, 0)
            thresholds = metric.get("thresholds", [])
            for t in thresholds:
                if t["min"] <= value <= t["max"]:
                    scores.append(t["score"])
                    break
        
        if not scores:
            return 0
        return round(sum(scores) / len(scores))

    def evaluate_scenarios(self, results, total_score):
        scenarios_config = self.config.get("scenarios", {})
        evaluations = {}
        
        for name, reqs in scenarios_config.items():
            # Estado inicial: 2 (Verde/Sucesso)
            state = 2 
            
            # Verificação de Pontuação Geral
            min_score = reqs.get("min_score", 0)
            if total_score < min_score:
                if total_score >= (min_score - 15): # Margem de tolerância para Amarelo
                    state = min(state, 1)
                else:
                    state = 0
            
            # Verificação de Download
            if "min_download" in reqs:
                val = results.get("download", 0)
                req = reqs["min_download"]
                if val < req:
                    if val >= (req * 0.7): # Tolerância de 30% para Amarelo
                        state = min(state, 1)
                    else:
                        state = 0

            # Verificação de Upload
            if state > 0 and "min_upload" in reqs:
                val = results.get("upload", 0)
                req = reqs["min_upload"]
                if val < req:
                    if val >= (req * 0.7):
                        state = min(state, 1)
                    else:
                        state = 0

            # Verificação de Ping (Menor é melhor)
            if state > 0 and "min_ping" in reqs:
                val = results.get("ping", 1000)
                req = reqs["min_ping"]
                if val > req:
                    if val <= (req * 1.4): # Tolerância de 40% para Amarelo
                        state = min(state, 1)
                    else:
                        state = 0
                
            # Verificação de Jitter (Menor é melhor)
            if state > 0 and "min_jitter" in reqs:
                val = results.get("jitter", 1000)
                req = reqs["min_jitter"]
                if val > req:
                    if val <= (req * 1.5):
                        state = min(state, 1)
                    else:
                        state = 0
                
            evaluations[name] = state
            
        return evaluations
