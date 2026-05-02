import os
import subprocess
import shlex
from typing import Dict, Any, List
from src.tools.base import BaseTool, ToolResult

SAFE_COMMANDS = {
    "nmap": ["-T4", "-F", "-sV", "-sC", "-oX", "-"],
    "ping": ["-n", "4", "-"],
    "traceroute": None,
    "nslookup": None,
    "dig": None,
    "curl": ["-s", "-I"],
    "whoami": None,
    "ipconfig": None,
    "netstat": ["-an"],
    "tasklist": None,
}

BLOCKED_COMMANDS = ["rm", "del", "format", "dd", "shutdown", "reboot", "init"]

class TerminalTool(BaseTool):
    def __init__(self, allowed_commands: List[str] = None, blocklist: List[str] = None):
        super().__init__("terminal", "Execute safe local terminal commands (nmap, network diagnostics)")
        self.allowed = allowed_commands or list(SAFE_COMMANDS.keys())
        self.blocklist = blocklist or BLOCKED_COMMANDS
    
    def execute(self, command: str, args: str = "", timeout: int = 30) -> ToolResult:
        self._record_usage()
        
        parts = shlex.split(f"{command} {args}") if args else shlex.split(command)
        if not parts:
            return ToolResult(success=False, output="", tool_name=self.name, error="Empty command")
        
        cmd_name = parts[0].lower()
        if cmd_name in self.blocklist:
            return ToolResult(success=False, output="", tool_name=self.name, error=f"Command '{cmd_name}' is blocked")
        
        if cmd_name not in self.allowed:
            return ToolResult(success=False, output="", tool_name=self.name, error=f"Command '{cmd_name}' not in allowlist")
        
        cmd_args = parts[1:]
        
        if cmd_name in SAFE_COMMANDS and SAFE_COMMANDS[cmd_name]:
            if cmd_args and not all(a in SAFE_COMMANDS[cmd_name] for a in cmd_args):
                return ToolResult(success=False, output="", tool_name=self.name, error=f"Unsafe arguments for {cmd_name}")
        
        try:
            result = subprocess.run(
                [cmd_name] + cmd_args,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False
            )
            
            output = result.stdout or result.stderr
            if not output:
                output = "(Command executed with no output)"
            
            return ToolResult(
                success=result.returncode == 0,
                output=output,
                tool_name=self.name,
                metadata={"return_code": result.returncode, "command": cmd_name}
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, output="", tool_name=self.name, error=f"Command timed out after {timeout}s")
        except FileNotFoundError:
            return ToolResult(success=False, output="", tool_name=self.name, error=f"Command '{cmd_name}' not found")
        except Exception as e:
            return ToolResult(success=False, output="", tool_name=self.name, error=str(e))
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "command": {"type": "string", "required": True, "description": "Command to execute (nmap, ping, etc.)"},
            "args": {"type": "string", "default": "", "description": "Command arguments"},
            "timeout": {"type": "integer", "default": 30}
        }