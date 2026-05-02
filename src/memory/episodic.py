from typing import List, Dict

class EpisodicMemory:
    def __init__(self, max_history: int = 10):
        self.history: List[Dict[str, str]] = []
        self.max_history = max_history

    def add_interaction(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_history * 2:  # *2 because user + assistant = 1 interaction
            self.history = self.history[-self.max_history * 2:]

    def get_history_string(self) -> str:
        return "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in self.history])

    def clear(self):
        self.history = []
