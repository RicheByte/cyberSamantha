"""
Unified LLM Provider — Hot-swap between Gemini (Cloud) and Ollama (Local).

Priority:
  1. If GEMINI_API_KEY is set → use Google Gemini API
  2. If OLLAMA_MODEL is set or Ollama is reachable → use local Ollama
  3. Fallback → embedding-only mode (no generation)

Environment variables:
  GEMINI_API_KEY   — Google Gemini API key
  OLLAMA_MODEL     — Ollama model name (default: "llama3")
  OLLAMA_BASE_URL  — Ollama server URL (default: "http://localhost:11434")
  LLM_PROVIDER     — Force provider: "gemini", "ollama", or "auto" (default: "auto")
"""

import os
import json
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class ProviderType(Enum):
    GEMINI = "gemini"
    OLLAMA = "ollama"
    NONE = "none"


@dataclass
class LLMResponse:
    """Standardized response from any LLM backend."""
    text: str
    provider: ProviderType
    model: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class LLMProvider:
    """
    Unified LLM interface that transparently routes to Gemini or Ollama.
    
    Usage:
        provider = LLMProvider()
        response = provider.generate("What is a zero-day exploit?")
        print(response.text)
        print(f"Answered by: {response.provider.value} / {response.model}")
    """

    def __init__(self):
        self.active_provider: ProviderType = ProviderType.NONE
        self.gemini_model = None
        self.ollama_model: str = ""
        self.ollama_base_url: str = ""
        self._initialize()

    def _initialize(self):
        """Detect and configure the best available LLM backend."""
        forced = os.getenv("LLM_PROVIDER", "auto").lower()

        if forced == "gemini" or (forced == "auto" and os.getenv("GEMINI_API_KEY")):
            if self._setup_gemini():
                return

        if forced == "ollama" or forced == "auto":
            if self._setup_ollama():
                return

        # Last resort: try Gemini anyway (in case forced=auto and no key)
        if forced == "auto" and self.active_provider == ProviderType.NONE:
            self._setup_gemini()

    # ── Gemini setup ─────────────────────────────────────────────────────
    def _setup_gemini(self) -> bool:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or genai is None:
            return False

        try:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")
            self.active_provider = ProviderType.GEMINI
            return True
        except Exception as e:
            print(f"⚠️  Gemini init failed: {e}")
            return False

    # ── Ollama setup ─────────────────────────────────────────────────────
    def _setup_ollama(self) -> bool:
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")

        try:
            resp = requests.get(f"{self.ollama_base_url}/api/tags", timeout=3)
            if resp.status_code == 200:
                available = [m["name"] for m in resp.json().get("models", [])]
                # Check if our desired model is available
                if available:
                    if self.ollama_model not in available and f"{self.ollama_model}:latest" not in available:
                        # Use the first available model
                        self.ollama_model = available[0].split(":")[0]
                    self.active_provider = ProviderType.OLLAMA
                    return True
        except (requests.ConnectionError, requests.Timeout):
            pass
        except Exception as e:
            print(f"⚠️  Ollama probe failed: {e}")
        return False

    # ── Unified generation ───────────────────────────────────────────────
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stop_sequences: List[str] = None,
        system_instruction: str = None,
    ) -> LLMResponse:
        """Generate text from the active LLM backend."""
        if self.active_provider == ProviderType.GEMINI:
            return self._generate_gemini(prompt, temperature, max_tokens, stop_sequences)
        elif self.active_provider == ProviderType.OLLAMA:
            return self._generate_ollama(prompt, temperature, max_tokens, stop_sequences, system_instruction)
        else:
            return LLMResponse(
                text="⚠️ No LLM backend available. Set GEMINI_API_KEY or start Ollama.",
                provider=ProviderType.NONE,
                model="none",
            )

    def _generate_gemini(
        self, prompt: str, temperature: float, max_tokens: int, stop_sequences: List[str] = None
    ) -> LLMResponse:
        config = {"temperature": temperature, "max_output_tokens": max_tokens}
        if stop_sequences:
            config["stop_sequences"] = stop_sequences
        try:
            response = self.gemini_model.generate_content(
                prompt, generation_config=config
            )
            return LLMResponse(
                text=response.text,
                provider=ProviderType.GEMINI,
                model="gemini-2.0-flash",
            )
        except Exception as e:
            return LLMResponse(
                text=f"Gemini error: {e}",
                provider=ProviderType.GEMINI,
                model="gemini-2.0-flash",
            )

    def _generate_ollama(
        self, prompt: str, temperature: float, max_tokens: int,
        stop_sequences: List[str] = None, system_instruction: str = None
    ) -> LLMResponse:
        payload: Dict[str, Any] = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if stop_sequences:
            payload["options"]["stop"] = stop_sequences
        if system_instruction:
            payload["system"] = system_instruction

        try:
            resp = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            return LLMResponse(
                text=data.get("response", ""),
                provider=ProviderType.OLLAMA,
                model=self.ollama_model,
                metadata={
                    "total_duration": data.get("total_duration"),
                    "eval_count": data.get("eval_count"),
                },
            )
        except Exception as e:
            return LLMResponse(
                text=f"Ollama error: {e}",
                provider=ProviderType.OLLAMA,
                model=self.ollama_model,
            )

    # ── Chat-style generation (for agents) ───────────────────────────────
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """
        Chat-style generation with message history.
        messages: [{"role": "user"/"assistant"/"system", "content": "..."}]
        """
        if self.active_provider == ProviderType.OLLAMA:
            return self._chat_ollama(messages, temperature, max_tokens)
        else:
            # Flatten to a single prompt for Gemini
            prompt = "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in messages)
            return self.generate(prompt, temperature, max_tokens)

    def _chat_ollama(
        self, messages: List[Dict[str, str]], temperature: float, max_tokens: int
    ) -> LLMResponse:
        payload = {
            "model": self.ollama_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        try:
            resp = requests.post(
                f"{self.ollama_base_url}/api/chat",
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            return LLMResponse(
                text=data.get("message", {}).get("content", ""),
                provider=ProviderType.OLLAMA,
                model=self.ollama_model,
            )
        except Exception as e:
            return LLMResponse(
                text=f"Ollama chat error: {e}",
                provider=ProviderType.OLLAMA,
                model=self.ollama_model,
            )

    # ── Utility ──────────────────────────────────────────────────────────
    @property
    def is_available(self) -> bool:
        return self.active_provider != ProviderType.NONE

    @property
    def provider_name(self) -> str:
        if self.active_provider == ProviderType.GEMINI:
            return "☁️  Gemini (gemini-2.0-flash)"
        elif self.active_provider == ProviderType.OLLAMA:
            return f"🏠 Ollama ({self.ollama_model})"
        return "❌ No LLM"

    def get_status(self) -> Dict[str, Any]:
        return {
            "provider": self.active_provider.value,
            "model": self.ollama_model if self.active_provider == ProviderType.OLLAMA else "gemini-2.0-flash",
            "available": self.is_available,
            "display_name": self.provider_name,
        }
