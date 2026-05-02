import os
from typing import Dict, Any
from src.tools.base import BaseTool, ToolResult

MAX_FILE_SIZE = 1024 * 1024

class FileReaderTool(BaseTool):
    def __init__(self, allowed_extensions: list = None):
        super().__init__("file_reader", "Read and analyze local files (code, configs, logs)")
        self.allowed_extensions = allowed_extensions or [".txt", ".md", ".py", ".js", ".json", ".yaml", ".yml", ".xml", ".sh", ".ps1", ".bat", ".conf", ".cfg", ".ini", ".log", ".c", ".cpp", ".h", ".go", ".rs", ".java"]
    
    def execute(self, file_path: str, max_lines: int = 500) -> ToolResult:
        self._record_usage()
        
        if not file_path:
            return ToolResult(success=False, output="", tool_name=self.name, error="No file path provided")
        
        abs_path = os.path.abspath(file_path)
        
        if not os.path.exists(abs_path):
            return ToolResult(success=False, output="", tool_name=self.name, error=f"File not found: {abs_path}")
        
        if not os.path.isfile(abs_path):
            return ToolResult(success=False, output="", tool_name=self.name, error=f"Not a file: {abs_path}")
        
        ext = os.path.splitext(abs_path)[1].lower()
        if ext not in self.allowed_extensions:
            return ToolResult(success=False, output="", tool_name=self.name, error=f"Extension '{ext}' not allowed")
        
        file_size = os.path.getsize(abs_path)
        if file_size > MAX_FILE_SIZE:
            return ToolResult(success=False, output="", tool_name=self.name, error=f"File too large: {file_size} bytes (max {MAX_FILE_SIZE})")
        
        try:
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        lines.append(f"\n... (truncated at {max_lines} lines)")
                        break
                    lines.append(line.rstrip())
            
            content = "\n".join(lines)
            
            ext = os.path.splitext(abs_path)[1]
            file_type = self._detect_file_type(abs_path, content)
            
            output = f"📄 File: {abs_path}\nType: {file_type}\nSize: {file_size} bytes\nLines: {min(i+1, max_lines)}\n\n```\n{content}\n```"
            
            return ToolResult(success=True, output=output, tool_name=self.name, metadata={"file_type": file_type, "lines": i+1})
        except UnicodeDecodeError:
            return ToolResult(success=False, output="", tool_name=self.name, error="Cannot read binary file")
        except PermissionError:
            return ToolResult(success=False, output="", tool_name=self.name, error="Permission denied")
        except Exception as e:
            return ToolResult(success=False, output="", tool_name=self.name, error=str(e))
    
    def _detect_file_type(self, path: str, content: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        name = os.path.basename(path).lower()
        
        if "dockerfile" in name:
            return "Dockerfile"
        elif ext == ".ps1":
            return "PowerShell"
        elif ext == ".py":
            return "Python"
        elif ext == ".js":
            return "JavaScript"
        elif ext == ".json":
            return "JSON"
        elif ext in [".yaml", ".yml"]:
            return "YAML"
        elif ext == ".xml":
            return "XML"
        elif content.startswith("#!"):
            return "Shell Script"
        elif content.startswith("package "):
            return "Go"
        elif "function" in content and "{" in content:
            return "C-family"
        return f"Text ({ext})"
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "file_path": {"type": "string", "required": True, "description": "Full path to file to read"},
            "max_lines": {"type": "integer", "default": 500, "description": "Maximum lines to read"}
        }