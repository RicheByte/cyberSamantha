import os
from typing import List, Dict

from src.core.llm_provider import LLMProvider

class EpisodicMemory:
    def __init__(self, max_history: int = 10):
        self.history: List[Dict[str, str]] = []
        self.max_history = max_history
        self.summary = ""

    def add_interaction(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_history * 2:  # *2 because user + assistant = 1 interaction
            self._summarize_and_decay()

    def _summarize_and_decay(self):
        """Summarize old memories to save tokens and avoid context overflow."""
        llm = LLMProvider()
        if not llm.is_available:
            # Fallback to simple truncation if no LLM
            self.history = self.history[-self.max_history * 2:]
            return

        # Take the oldest half of the history to summarize
        half_point = self.max_history
        old_history = self.history[:half_point]
        new_history = self.history[half_point:]

        history_str = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in old_history])
        prompt = f"Summarize the key points of the following conversation history. Current summary: {self.summary}\n\nNew interactions to incorporate:\n{history_str}"
        
        try:
            response = llm.generate(prompt, temperature=0.3, max_tokens=512)
            self.summary = response.text
        except Exception as e:
            print(f"Memory summarization failed: {e}")
        
        self.history = new_history

    def get_history_string(self) -> str:
        base_str = ""
        if self.summary:
            base_str = f"[Previous Conversation Summary]: {self.summary}\n---\n"
        return base_str + "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in self.history])

    def clear(self):
        self.history = []
        self.summary = ""
