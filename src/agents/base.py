import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable

try:
    import google.generativeai as genai
    from google.generativeai.types import content_types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

import functools
import time
from src.core.llm_provider import LLMProvider, ProviderType
from src.skills.loader import SkillLoader
from src.skills.genome_engine import GenomeEngine


class BaseAgent(ABC):
    """
    Base class for specialized sub-agents (HackerAgent, ResearcherAgent, etc.).
    
    When Gemini API is available, uses native function calling for maximum
    reliability. Falls back to Ollama chat-style interaction when running locally.
    
    Agents automatically load compatible skills from:
      - skills/*.md — markdown playbooks injected into the system prompt
      - src/skills/*.py — Python tool functions added to the tool list
    """

    # Shared loaders (singleton across all agents)
    _skill_loader: SkillLoader = None
    _genome_engine: GenomeEngine = None

    def __init__(self, name: str, description: str, system_prompt: str):
        self.name = name
        self.description = description
        self._base_system_prompt = system_prompt
        self.llm = LLMProvider()
        self.model = None
        self.chat_session = None

        # Initialize shared loaders
        if BaseAgent._skill_loader is None:
            BaseAgent._skill_loader = SkillLoader()
            BaseAgent._skill_loader.discover()
        if BaseAgent._genome_engine is None:
            BaseAgent._genome_engine = GenomeEngine()

        # Build full system prompt with skill instructions
        self.system_prompt = self._build_system_prompt()
        self._setup_model()

    @classmethod
    def get_skill_loader(cls) -> SkillLoader:
        """Get the shared skill loader instance."""
        if cls._skill_loader is None:
            cls._skill_loader = SkillLoader()
            cls._skill_loader.discover()
        return cls._skill_loader

    @classmethod
    def get_genome_engine(cls) -> GenomeEngine:
        if cls._genome_engine is None:
            cls._genome_engine = GenomeEngine()
        return cls._genome_engine

    def _build_system_prompt(self) -> str:
        """Combine the base system prompt with loaded markdown skill instructions."""
        prompt = self._base_system_prompt

        # Inject compatible markdown skill instructions
        skill_instructions = BaseAgent._skill_loader.get_skill_instructions(self.name)
        if skill_instructions:
            prompt += f"\n{skill_instructions}"

        return prompt

    def _setup_model(self):
        """
        If Gemini is the active provider, use native function calling.
        If Ollama, we'll use a chat-based ReAct loop instead.
        """
        if self.llm.active_provider == ProviderType.GEMINI and HAS_GENAI:
            try:
                tools = self._get_all_tools()
                self.model = genai.GenerativeModel(
                    model_name='gemini-2.0-flash',
                    system_instruction=self.system_prompt,
                    tools=tools if tools else None
                )
                self.chat_session = self.model.start_chat(enable_automatic_function_calling=True)
            except Exception as e:
                print(f"⚠️ {self.name}: Gemini function-calling setup failed: {e}")

    def _get_all_tools(self) -> List[Callable]:
        """Combine agent's own tools with compatible Python skill tools."""
        tools = self.get_tools()

        # Add tools from compatible Python skills, wrapped to track metrics
        skill_tools = BaseAgent._skill_loader.get_all_tools(self.name)
        if skill_tools:
            genome = self.get_genome_engine()
            for tool_fn in skill_tools:
                tools.append(self._wrap_skill_tool(tool_fn, genome))

        return tools

    def _wrap_skill_tool(self, tool_fn: Callable, genome_engine: GenomeEngine) -> Callable:
        """Wraps a tool to track execution time and success rate for the Genome Engine."""
        @functools.wraps(tool_fn)
        def wrapper(*args, **kwargs):
            start = time.time()
            success = True
            try:
                result = tool_fn(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise e
            finally:
                duration = time.time() - start
                genome_engine.record_usage(tool_fn.__name__, success, duration)
        return wrapper

    @abstractmethod
    def get_tools(self) -> List[Callable]:
        """Return a list of python functions that Gemini can call natively."""
        return []

    def run(self, query: str) -> str:
        """Run the agent on a query. Routes to the best available backend."""
        md_skills = self.get_skill_loader().get_md_skills_for(self.name)
        start_time = time.time()
        success = True

        # Prefer Gemini native function calling
        if self.chat_session:
            try:
                response = self.chat_session.send_message(query)
                return response.text
            except Exception as e:
                success = False
                return f"Error in {self.name} (Gemini): {str(e)}"
            finally:
                duration = time.time() - start_time
                for s in md_skills:
                    self.get_genome_engine().record_usage(s.name, success, duration)

        # Fallback: Ollama chat with tool descriptions in the system prompt
        if self.llm.active_provider == ProviderType.OLLAMA:
            try:
                result = self._run_ollama_fallback(query)
                return result
            except Exception as e:
                success = False
                raise e
            finally:
                duration = time.time() - start_time
                for s in md_skills:
                    self.get_genome_engine().record_usage(s.name, success, duration)

        return f"{self.name} is disabled (No LLM backend available)."

    def _run_ollama_fallback(self, query: str) -> str:
        """
        For Ollama, embed tool descriptions in the system prompt and let
        the model generate structured responses we can parse.
        """
        tools_desc = self._get_tools_description()
        messages = [
            {
                "role": "system",
                "content": f"{self.system_prompt}\n\nYou have access to these tools:\n{tools_desc}\n\n"
                           f"To use a tool, respond with:\nTOOL_CALL: <function_name>(<args>)\n"
                           f"Otherwise, respond normally."
            },
            {"role": "user", "content": query},
        ]

        response = self.llm.chat(messages, temperature=0.3, max_tokens=1024)

        # Try to detect and execute tool calls from the response
        if "TOOL_CALL:" in response.text:
            return self._execute_ollama_tool_call(response.text, messages)

        return response.text

    def _get_tools_description(self) -> str:
        """Generate a text description of available tools for Ollama."""
        tools = self._get_all_tools()
        if not tools:
            return "No tools available."

        descriptions = []
        for tool_fn in tools:
            name = tool_fn.__name__
            doc = tool_fn.__doc__ or "No description"
            descriptions.append(f"  - {name}: {doc.strip()}")

        return "\n".join(descriptions)

    def _execute_ollama_tool_call(self, response_text: str, messages: list) -> str:
        """Parse and execute a tool call from Ollama's text response."""
        try:
            # Extract the TOOL_CALL line
            for line in response_text.split("\n"):
                if line.strip().startswith("TOOL_CALL:"):
                    call_str = line.split("TOOL_CALL:", 1)[1].strip()
                    # Simple parsing: function_name(arg1, arg2)
                    func_name = call_str.split("(")[0].strip()
                    args_str = call_str.split("(", 1)[1].rsplit(")", 1)[0]

                    # Find and execute the matching tool
                    tools = self._get_all_tools()
                    for tool_fn in tools:
                        if tool_fn.__name__ == func_name:
                            # Parse arguments (simple key=value or positional)
                            args = [a.strip().strip('"').strip("'") for a in args_str.split(",") if a.strip()]
                            result = tool_fn(*args) if args else tool_fn()

                            # Feed the result back
                            messages.append({"role": "assistant", "content": response_text})
                            messages.append({"role": "user", "content": f"Tool result:\n{result}\n\nNow provide your final analysis."})
                            final = self.llm.chat(messages, temperature=0.3, max_tokens=1024)
                            return final.text

            return response_text
        except Exception as e:
            return f"Error executing tool call: {e}\n\nOriginal response:\n{response_text}"

    def get_loaded_skills(self) -> List[Dict[str, Any]]:
        """Return info about all skills loaded for this agent."""
        md_skills = BaseAgent._skill_loader.get_md_skills_for(self.name)
        py_skills = BaseAgent._skill_loader.get_py_skills_for(self.name)
        return [s.get_info() for s in md_skills] + [s.get_info() for s in py_skills]
