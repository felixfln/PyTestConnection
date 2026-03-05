import json
import os

class QualityCalculator:
    def __init__(self, config_path="config/metrics_config.json"):
        self.config = self._load_config(config_path)

    def _load_config(self, path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"metrics": {}, "scenarios": {}}

    def calculate_score(self, results):
        metrics_config = self.config.get("metrics", {})
        scores = []
        
        for key, metric in metrics_config.items():
            value = results.get(key, 0)
            thresholds = metric.get("thresholds", [])
            for t in thresholds:
                if t["min"] <= value < t["max"]:
                    scores.append(t["score"])
                    break
        
        if not scores:
            return 0
        return int(sum(scores) / len(scores))

    def evaluate_scenarios(self, results, total_score):
        scenarios_config = self.config.get("scenarios", {})
        evaluations = {}
        
        for name, reqs in scenarios_config.items():
            is_ok = True
            if total_score < reqs.get("min_score", 0):
                is_ok = False
            
            if is_ok and "min_download" in reqs and results.get("download", 0) < reqs["min_download"]:
                is_ok = False
            
            if is_ok and "min_ping" in reqs and results.get("ping", 1000) > reqs["min_ping"]:
                is_ok = False
                
            if is_ok and "min_jitter" in reqs and results.get("jitter", 1000) > reqs["min_jitter"]:
                is_ok = False

            if is_ok and "min_upload" in reqs and results.get("upload", 0) < reqs["min_upload"]:
                is_ok = False
                
            evaluations[name] = 1 if is_ok else 0
            
        return evaluations
