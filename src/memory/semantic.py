import os
import json
from typing import Dict, Any, List

class SemanticMemory:
    def __init__(self, memory_path: str = "data/memory.json"):
        self.memory_path = memory_path
        self.facts: Dict[str, Any] = {}
        self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, 'r', encoding='utf-8') as f:
                    self.facts = json.load(f)
            except Exception as e:
                print(f"Error loading semantic memory: {e}")

    def _save_memory(self):
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        try:
            with open(self.memory_path, 'w', encoding='utf-8') as f:
                json.dump(self.facts, f, indent=2)
        except Exception as e:
            print(f"Error saving semantic memory: {e}")

    def add_fact(self, key: str, value: Any):
        self.facts[key] = value
        self._save_memory()

    def get_fact(self, key: str) -> Any:
        return self.facts.get(key)
        
    def get_all_facts(self) -> Dict[str, Any]:
        return self.facts
