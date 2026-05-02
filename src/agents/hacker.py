from typing import List, Callable
from src.agents.base import BaseAgent
from src.tools.terminal import TerminalTool

class HackerAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are CyberSamantha's Offensive Security Agent (HackerAgent).
You specialize in reconnaissance, vulnerability assessment, and exploiting (in authorized scopes).
You have access to a safe local terminal to run commands like nmap, curl, and network diagnostics.
Your goal is to provide deep technical insights into target infrastructure.
Always execute actions safely and provide detailed technical writeups of the output."""
        super().__init__(
            name="HackerAgent",
            description="Specializes in offensive security, network scanning, and reconnaissance.",
            system_prompt=system_prompt
        )
        self.terminal = TerminalTool()

    def get_tools(self) -> List[Callable]:
        def run_network_scan(target_ip: str, scan_type: str = "quick") -> str:
            """
            Run an nmap network scan against a target IP or domain.
            
            Args:
                target_ip: The IP address or domain to scan.
                scan_type: Type of scan ('quick', 'ports', 'vuln').
            """
            args = "-F"
            if scan_type == "ports":
                args = "-p- -T4"
            elif scan_type == "vuln":
                args = "-sV -sC"
            
            result = self.terminal.execute("nmap", f"{args} {target_ip}")
            return result.output if result.success else f"Error: {result.error}\nOutput: {result.output}"
            
        def check_headers(url: str) -> str:
            """
            Fetch HTTP headers to check for security misconfigurations.
            
            Args:
                url: The full URL to check (e.g., https://example.com)
            """
            result = self.terminal.execute("curl", f"-s -I {url}")
            return result.output if result.success else f"Error: {result.error}"

        return [run_network_scan, check_headers]
