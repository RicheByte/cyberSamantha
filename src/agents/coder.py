from typing import List, Callable

from src.agents.base import BaseAgent
from src.tools.terminal import TerminalTool
from src.tools.file_reader import FileReaderTool


class CoderAgent(BaseAgent):
    """
    Coder Agent — Specializes in reading, analyzing, and debugging local code
    and configuration files. Can run safe terminal commands for code analysis.
    """

    def __init__(self):
        system_prompt = """You are CyberSamantha's Code Analysis Agent (CoderAgent).
You specialize in:
1. Reading and analyzing source code, configuration files, and scripts.
2. Finding security vulnerabilities in code (code review).
3. Running safe analysis commands (grep, find, file inspection).
4. Explaining complex codebases and suggesting improvements.

You have access to a safe local terminal and a file reader.
Always provide detailed technical explanations with code snippets when relevant.
When reviewing code for security issues, use OWASP and CWE references."""
        super().__init__(
            name="CoderAgent",
            description="Specializes in code analysis, security review, and local file inspection.",
            system_prompt=system_prompt,
        )
        self.terminal = TerminalTool()
        self.file_reader = FileReaderTool()

    def get_tools(self) -> List[Callable]:
        def read_source_file(file_path: str) -> str:
            """
            Read and return the contents of a local source code or config file.
            
            Args:
                file_path: Full path to the file to read.
            """
            result = self.file_reader.execute(file_path=file_path)
            return result.output if result.success else f"Error: {result.error}"

        def analyze_directory(directory_path: str) -> str:
            """
            List files in a directory to understand project structure.
            
            Args:
                directory_path: Path to the directory to analyze.
            """
            import os
            try:
                entries = []
                for root, dirs, files in os.walk(directory_path):
                    depth = root.replace(directory_path, '').count(os.sep)
                    if depth > 2:
                        continue  # Don't go too deep
                    indent = "  " * depth
                    entries.append(f"{indent}{os.path.basename(root)}/")
                    for f in files[:20]:  # Cap at 20 files per dir
                        entries.append(f"{indent}  {f}")
                return "\n".join(entries[:100])  # Cap total output
            except Exception as e:
                return f"Error: {e}"

        def run_analysis_command(command: str) -> str:
            """
            Run a safe terminal command for code analysis (e.g., grep, find).
            
            Args:
                command: The analysis command to run.
            """
            result = self.terminal.execute(command=command)
            return result.output if result.success else f"Error: {result.error}"

        return [read_source_file, analyze_directory, run_analysis_command]
