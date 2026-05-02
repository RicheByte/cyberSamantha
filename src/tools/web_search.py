import os
import json
from typing import Dict, Any
from src.tools.base import BaseTool, ToolResult

try:
    from exa_py import Exa
except ImportError:
    Exa = None

class WebSearchTool(BaseTool):
    def __init__(self, api_key: str = None):
        super().__init__("web_search", "Search the web for cybersecurity threat intel, vulnerabilities, and current events")
        self.api_key = api_key or os.getenv("EXA_API_KEY")
        self.client = None
        if self.api_key and Exa:
            try:
                self.client = Exa(self.api_key)
            except Exception as e:
                print(f"⚠️  Exa API init failed: {e}")
    
    def execute(self, query: str,num_results: int = 5, category: str = None) -> ToolResult:
        self._record_usage()
        
        if not self.client:
            return ToolResult(
                success=False,
                output="",
                tool_name=self.name,
                error="EXA_API_KEY not set or Exa package not installed"
            )
        
        try:
            search_opts = {"num_results": num_results}
            if category:
                search_opts["category"] = category
            
            results = self.client.search(query, **search_opts)
            
            output_parts = []
            for r in results.results:
                output_parts.append(f"## {r.title}\n{r.url}\n{r.snippet}\n")
            
            output = f"🔍 Search results for: {query}\n\n" + "\n---\n".join(output_parts)
            
            return ToolResult(
                success=True,
                output=output,
                tool_name=self.name,
                metadata={"results_count": len(results.results), "query": query}
            )
        except Exception as e:
            return ToolResult(success=False, output="", tool_name=self.name, error=str(e))
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "query": {"type": "string", "required": True, "description": "Search query"},
            "num_results": {"type": "integer", "default": 5},
            "category": {"type": "string", "default": None}
        }