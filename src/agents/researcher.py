from typing import List, Callable

from src.agents.base import BaseAgent
from src.tools.web_search import WebSearchTool


class ResearcherAgent(BaseAgent):
    """
    Researcher Agent — Specializes in web research, reading articles,
    and synthesizing threat intelligence from external sources.
    """

    def __init__(self):
        system_prompt = """You are CyberSamantha's Research Agent (ResearcherAgent).
You specialize in deep web research, threat intelligence gathering, and synthesizing
information from external cybersecurity sources like CVE databases, security blogs,
and advisory feeds.

Your goal is to:
1. Search the web for the latest threat intel, CVEs, and security advisories.
2. Read and analyze article content to extract actionable intelligence.
3. Provide detailed, well-sourced technical summaries.

Always cite your sources and provide context about the reliability of the information."""
        super().__init__(
            name="ResearcherAgent",
            description="Specializes in web research, threat intelligence, and article analysis.",
            system_prompt=system_prompt,
        )
        self.web_search = WebSearchTool()

    def get_tools(self) -> List[Callable]:
        def search_threat_intel(query: str) -> str:
            """
            Search the web for cybersecurity threat intelligence, CVEs, or advisories.
            
            Args:
                query: The search query (e.g., "CVE-2024-1234", "Log4j exploit")
            """
            result = self.web_search.execute(query=query, num_results=5)
            return result.output if result.success else f"Error: {result.error}"

        def search_cve(cve_id: str) -> str:
            """
            Search specifically for a CVE identifier and its details.
            
            Args:
                cve_id: The CVE identifier (e.g., "CVE-2024-1234")
            """
            result = self.web_search.execute(
                query=f"{cve_id} vulnerability details exploit",
                num_results=3,
            )
            return result.output if result.success else f"Error: {result.error}"

        return [search_threat_intel, search_cve]
