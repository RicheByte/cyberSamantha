"""
SkillLoader — Discovers and loads markdown-based skill files + Python skill modules.

Two types of skills:
  1. **Markdown Skills** (primary) — .md files in the `skills/` project folder.
     Agents load these as instruction playbooks injected into their system prompt.
  2. **Python Skills** (optional) — BaseSkill subclasses in `src/skills/`.
     Provide callable tool functions agents can execute.

Markdown skill files must contain a `## Skill Info` section with:
  - **Name:** skill_id
  - **Agent:** AgentName (or "all")
  - **Tags:** tag1, tag2
"""

import os
import re
import importlib
import inspect
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

from src.skills.base import BaseSkill


# ── Markdown Skill representation ────────────────────────────────────────

class MarkdownSkill:
    """A skill loaded from a .md file — acts as an instruction playbook."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.name: str = ""
        self.description: str = ""
        self.agent: str = "all"
        self.tags: List[str] = []
        self.content: str = ""
        self.enabled: bool = True
        self._parse()

    def _parse(self):
        """Read and parse the markdown skill file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.content = f.read()
        except Exception as e:
            self.content = ""
            self.name = self.file_name.replace(".md", "")
            return

        # Extract title from first H1
        title_match = re.search(r"^#\s+(.+)$", self.content, re.MULTILINE)
        if title_match:
            # Strip emoji and whitespace
            raw_title = title_match.group(1).strip()
            self.description = re.sub(r"[^\w\s\-—/&]", "", raw_title).strip()

        # Parse ## Skill Info block
        info_match = re.search(
            r"##\s+Skill Info\s*\n(.*?)(?=\n##|\Z)",
            self.content,
            re.DOTALL,
        )
        if info_match:
            info_block = info_match.group(1)

            name_match = re.search(r"\*\*Name:\*\*\s*(.+)", info_block)
            if name_match:
                self.name = name_match.group(1).strip()

            agent_match = re.search(r"\*\*Agent:\*\*\s*(.+)", info_block)
            if agent_match:
                self.agent = agent_match.group(1).strip()

            tags_match = re.search(r"\*\*Tags:\*\*\s*(.+)", info_block)
            if tags_match:
                self.tags = [t.strip() for t in tags_match.group(1).split(",")]

        if not self.name:
            self.name = self.file_name.replace(".md", "")

    def is_compatible_with(self, agent_name: str) -> bool:
        """Check if this skill applies to a given agent."""
        if self.agent.lower() == "all":
            return True
        return agent_name.lower() == self.agent.lower()

    def get_instructions(self) -> str:
        """Return the full markdown content for prompt injection."""
        return self.content

    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "type": "markdown",
            "agent": self.agent,
            "tags": self.tags,
            "enabled": self.enabled,
            "file": self.file_name,
        }

    def __repr__(self):
        return f"<MarkdownSkill:{self.name} ({self.file_name})>"


# ── Unified Skill Loader ────────────────────────────────────────────────

class SkillLoader:
    """
    Discovers, loads, and manages both markdown and Python skills.

    Usage:
        loader = SkillLoader()
        loader.discover()

        # Get markdown skills for an agent
        skills = loader.get_md_skills_for("HackerAgent")
        for s in skills:
            print(s.get_instructions())

        # Get Python tool functions for an agent
        tools = loader.get_all_tools("CoderAgent")

        # CLI summary
        loader.get_summary()
    """

    def __init__(self, skills_dir: str = None):
        self._md_skills: Dict[str, MarkdownSkill] = {}
        self._py_skills: Dict[str, BaseSkill] = {}
        self._skills_dir = skills_dir  # For .md files
        self._discovered = False

    def discover(self, md_skills_dir: str = None, py_skills_dir: str = None):
        """Discover both markdown and Python skills."""
        self._discover_md_skills(md_skills_dir or self._skills_dir)
        self._discover_py_skills(py_skills_dir)
        self._discovered = True

    def _discover_md_skills(self, skills_dir: str = None):
        """Scan the project's skills/ folder for .md files."""
        if skills_dir is None:
            # Default: project_root/skills/
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            skills_dir = os.path.join(project_root, "skills")

        if not os.path.isdir(skills_dir):
            return

        for filename in os.listdir(skills_dir):
            if not filename.endswith(".md"):
                continue

            file_path = os.path.join(skills_dir, filename)
            try:
                skill = MarkdownSkill(file_path)
                self._md_skills[skill.name] = skill
            except Exception as e:
                print(f"⚠️  Failed to load markdown skill {filename}: {e}")

    def _discover_py_skills(self, py_skills_dir: str = None):
        """Scan src/skills/ for Python BaseSkill subclasses."""
        if py_skills_dir is None:
            py_skills_dir = os.path.dirname(os.path.abspath(__file__))

        skip_files = {"__init__.py", "base.py", "loader.py"}

        for filename in os.listdir(py_skills_dir):
            if not filename.endswith(".py") or filename in skip_files or filename.startswith("_"):
                continue

            module_name = f"src.skills.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        inspect.isclass(attr)
                        and issubclass(attr, BaseSkill)
                        and attr is not BaseSkill
                    ):
                        instance = attr()
                        self._py_skills[instance.name] = instance
            except Exception as e:
                print(f"⚠️  Failed to load Python skill from {filename}: {e}")

    def _ensure_discovered(self):
        if not self._discovered:
            self.discover()

    # ── Markdown skill queries ───────────────────────────────────────

    def get_md_skill(self, name: str) -> Optional[MarkdownSkill]:
        self._ensure_discovered()
        return self._md_skills.get(name)

    def get_all_md_skills(self) -> List[MarkdownSkill]:
        self._ensure_discovered()
        return list(self._md_skills.values())

    def get_md_skills_for(self, agent_name: str) -> List[MarkdownSkill]:
        """Get markdown skills compatible with a specific agent."""
        self._ensure_discovered()
        return [
            s for s in self._md_skills.values()
            if s.enabled and s.is_compatible_with(agent_name)
        ]

    def get_skill_instructions(self, agent_name: str) -> str:
        """
        Build a combined instruction block from all compatible markdown skills.
        This is what gets injected into an agent's system prompt.
        """
        skills = self.get_md_skills_for(agent_name)
        if not skills:
            return ""

        parts = ["\n\n--- LOADED SKILLS ---\n"]
        for skill in skills:
            parts.append(f"\n{'='*40}\n[Skill: {skill.name}]\n{'='*40}\n")
            parts.append(skill.get_instructions())
        parts.append("\n--- END SKILLS ---\n")

        return "\n".join(parts)

    # ── Python skill queries ─────────────────────────────────────────

    def get_py_skill(self, name: str) -> Optional[BaseSkill]:
        self._ensure_discovered()
        return self._py_skills.get(name)

    def get_all_py_skills(self) -> List[BaseSkill]:
        self._ensure_discovered()
        return list(self._py_skills.values())

    def get_py_skills_for(self, agent_name: str) -> List[BaseSkill]:
        self._ensure_discovered()
        return [
            s for s in self._py_skills.values()
            if s.enabled and s.is_compatible_with(agent_name)
        ]

    def get_all_tools(self, agent_name: str = None) -> List[Callable]:
        """Get all callable tool functions from Python skills."""
        self._ensure_discovered()
        tools = []
        skills = self.get_py_skills_for(agent_name) if agent_name else self.get_all_py_skills()
        for skill in skills:
            if skill.enabled:
                tools.extend(skill.get_tools())
        return tools

    # ── Management ───────────────────────────────────────────────────

    def enable(self, skill_name: str) -> bool:
        skill = self._md_skills.get(skill_name) or self._py_skills.get(skill_name)
        if skill:
            skill.enabled = True
            return True
        return False

    def disable(self, skill_name: str) -> bool:
        skill = self._md_skills.get(skill_name) or self._py_skills.get(skill_name)
        if skill:
            skill.enabled = False
            return True
        return False

    # ── Summary ──────────────────────────────────────────────────────

    def get_summary(self) -> List[Dict[str, Any]]:
        """Get a combined summary of all skills (md + py)."""
        self._ensure_discovered()
        items = []
        for s in self._md_skills.values():
            items.append(s.get_info())
        for s in self._py_skills.values():
            info = s.get_info()
            info["type"] = "python"
            items.append(info)
        return items

    @property
    def count(self) -> int:
        self._ensure_discovered()
        return len(self._md_skills) + len(self._py_skills)

    def __repr__(self):
        self._ensure_discovered()
        return f"<SkillLoader: {len(self._md_skills)} md + {len(self._py_skills)} py skills>"
