import os
import json
from typing import Dict, Any, List

class MetaMemory:
    """
    Self-Reflective Loop Memory tier.
    Tracks execution tracing of multi-agent interactions and strategy success rates.
    """
    def __init__(self, memory_path: str = "data/meta_memory.json"):
        self.memory_path = memory_path
        self.strategies: List[Dict[str, Any]] = []
        self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, 'r', encoding='utf-8') as f:
                    self.strategies = json.load(f)
            except Exception as e:
                print(f"Error loading meta memory: {e}")

    def _save_memory(self):
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        try:
            with open(self.memory_path, 'w', encoding='utf-8') as f:
                json.dump(self.strategies, f, indent=2)
        except Exception as e:
            print(f"Error saving meta memory: {e}")

    def log_strategy_execution(self, task_type: str, strategy: str, agents_used: List[str], outcome_score: float, context: str = ""):
        """
        Logs a reasoning strategy and its outcome.
        """
        entry = {
            "task_type": task_type,
            "strategy": strategy,
            "agents_used": agents_used,
            "outcome_score": outcome_score,
            "context": context
        }
        self.strategies.append(entry)
        self._save_memory()

    def query_best_strategy(self, task_type: str) -> Dict[str, Any]:
        """
        Retrieves the most successful strategy for a given task type.
        """
        relevant = [s for s in self.strategies if s.get("task_type") == task_type]
        if not relevant:
            return {"strategy": "linear_delegation", "expected_score": 0.5}
        
        # Sort by outcome score
        best = sorted(relevant, key=lambda x: x.get("outcome_score", 0), reverse=True)[0]
        return best
