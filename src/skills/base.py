"""
BaseSkill — Abstract interface for all pluggable agent skills.

A skill is a self-contained capability module that agents can load at runtime.
Each skill declares:
  - name / description / version
  - A set of callable functions (tools) it exposes
  - Which agent types it's compatible with (or "all")

Skills are discovered automatically from the `src/skills/` directory.
Drop a new .py file there → agents can use it immediately.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SkillResult:
    """Standardized result returned by a skill function."""
    success: bool
    output: str
    skill_name: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseSkill(ABC):
    """
    Abstract base class for all CyberSamantha skills.

    To create a new skill:
      1. Create a file in src/skills/ (e.g., my_skill.py)
      2. Subclass BaseSkill
      3. Implement get_tools() returning a list of callable functions
      4. The skill is auto-discovered and available to agents

    Example:
        class MySkill(BaseSkill):
            name = "my_skill"
            description = "Does something cool"
            version = "1.0"

            def get_tools(self) -> List[Callable]:
                def do_thing(input: str) -> str:
                    '''Does the thing.'''
                    return f"Did: {input}"
                return [do_thing]
    """

    # ── Subclasses MUST set these ─────────────────────────────────────
    name: str = "unnamed_skill"
    description: str = "No description"
    version: str = "0.1"

    # Which agent names this skill is compatible with. Empty set = all agents.
    compatible_agents: Set[str] = set()

    # Tags for categorization and search
    tags: List[str] = []

    def __init__(self):
        self.enabled: bool = True
        self.usage_count: int = 0
        self.last_used: Optional[datetime] = None

    @abstractmethod
    def get_tools(self) -> List[Callable]:
        """
        Return a list of plain Python functions that this skill provides.
        Each function should have a descriptive docstring (used by agents).
        """
        return []

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Generate schema descriptions for all tools in this skill."""
        schemas = []
        for fn in self.get_tools():
            import inspect
            sig = inspect.signature(fn)
            params = {}
            for pname, param in sig.parameters.items():
                ptype = "string"
                if param.annotation != inspect.Parameter.empty:
                    ptype = param.annotation.__name__ if hasattr(param.annotation, '__name__') else str(param.annotation)
                params[pname] = {
                    "type": ptype,
                    "required": param.default == inspect.Parameter.empty,
                }
                if param.default != inspect.Parameter.empty:
                    params[pname]["default"] = param.default

            schemas.append({
                "name": fn.__name__,
                "description": (fn.__doc__ or "No description").strip(),
                "parameters": params,
                "skill": self.name,
            })
        return schemas

    def is_compatible_with(self, agent_name: str) -> bool:
        """Check if this skill can be used by a given agent."""
        if not self.compatible_agents:
            return True  # Empty set = compatible with all
        return agent_name in self.compatible_agents

    def record_usage(self):
        self.usage_count += 1
        self.last_used = datetime.now()

    def get_info(self) -> Dict[str, Any]:
        """Return a summary dict about this skill."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "enabled": self.enabled,
            "tags": self.tags,
            "compatible_agents": list(self.compatible_agents) or ["all"],
            "tools": [fn.__name__ for fn in self.get_tools()],
            "usage_count": self.usage_count,
        }

    def __repr__(self):
        return f"<Skill:{self.name} v{self.version} ({len(self.get_tools())} tools)>"
