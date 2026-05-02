from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ToolResult:
    success: bool
    output: str
    tool_name: str
    error: str = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseTool(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.usage_count = 0
        self.last_used = None
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self._get_parameters_schema()
        }
    
    @abstractmethod
    def _get_parameters_schema(self) -> Dict[str, Any]:
        pass
    
    def _record_usage(self):
        self.usage_count += 1
        self.last_used = datetime.now()