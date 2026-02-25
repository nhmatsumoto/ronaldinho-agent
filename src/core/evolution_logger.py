import os
import datetime

class EvolutionLogger:
    def __init__(self, log_path=".agent/evolution.log"):
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def log_event(self, provider, model_id, status, error=None):
        """Logs a model interaction event."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_msg = f" | Error: {error}" if error else ""
        log_entry = f"[{timestamp}] Provider: {provider} | Model: {model_id} | Status: {status}{error_msg}\n"
        
        with open(self.log_path, "a") as f:
            f.write(log_entry)

evolution_logger = EvolutionLogger()
