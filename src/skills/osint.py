"""
OSINT Skill — Open Source Intelligence gathering utilities.

Provides tools for DNS lookups, WHOIS info, IP geolocation,
and subdomain enumeration using safe local commands.
"""

from typing import List, Callable
import subprocess
import socket
import json

from src.skills.base import BaseSkill, SkillResult


class OsintSkill(BaseSkill):
    name = "osint"
    description = "Open Source Intelligence — DNS, WHOIS, IP lookups, and subdomain enumeration"
    version = "1.0"
    tags = ["recon", "network", "intelligence"]
    compatible_agents = {"HackerAgent", "ResearcherAgent"}

    def get_tools(self) -> List[Callable]:

        def dns_lookup(domain: str) -> str:
            """
            Perform a DNS lookup on a domain to resolve IPs and records.

            Args:
                domain: The domain name to look up (e.g., "example.com")
            """
            try:
                results = []
                # A records
                try:
                    ips = socket.getaddrinfo(domain, None, socket.AF_INET)
                    a_records = list(set(ip[4][0] for ip in ips))
                    results.append(f"A Records: {', '.join(a_records)}")
                except socket.gaierror:
                    results.append("A Records: None found")

                # AAAA records
                try:
                    ips6 = socket.getaddrinfo(domain, None, socket.AF_INET6)
                    aaaa_records = list(set(ip[4][0] for ip in ips6))
                    results.append(f"AAAA Records: {', '.join(aaaa_records)}")
                except socket.gaierror:
                    pass

                # Try nslookup for more detail
                try:
                    proc = subprocess.run(
                        ["nslookup", domain],
                        capture_output=True, text=True, timeout=10
                    )
                    if proc.stdout:
                        results.append(f"\nnslookup output:\n{proc.stdout}")
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    pass

                return "\n".join(results) if results else "No DNS records found."
            except Exception as e:
                return f"DNS lookup error: {e}"

        def reverse_dns(ip_address: str) -> str:
            """
            Perform a reverse DNS lookup on an IP address.

            Args:
                ip_address: The IP address to reverse-lookup (e.g., "8.8.8.8")
            """
            try:
                hostname, _, _ = socket.gethostbyaddr(ip_address)
                return f"Reverse DNS for {ip_address}: {hostname}"
            except socket.herror:
                return f"No reverse DNS record found for {ip_address}"
            except Exception as e:
                return f"Reverse DNS error: {e}"

        def port_check(host: str, port: str) -> str:
            """
            Check if a specific TCP port is open on a host.

            Args:
                host: The hostname or IP to check.
                port: The port number to check (e.g., "443").
            """
            try:
                port_int = int(port)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, port_int))
                sock.close()
                if result == 0:
                    return f"Port {port_int} on {host}: OPEN ✅"
                else:
                    return f"Port {port_int} on {host}: CLOSED ❌"
            except ValueError:
                return f"Invalid port number: {port}"
            except Exception as e:
                return f"Port check error: {e}"

        def whois_lookup(domain: str) -> str:
            """
            Attempt a WHOIS lookup using the local whois command.

            Args:
                domain: The domain to look up (e.g., "example.com")
            """
            try:
                proc = subprocess.run(
                    ["whois", domain],
                    capture_output=True, text=True, timeout=15
                )
                output = proc.stdout or proc.stderr
                # Truncate if too long
                if len(output) > 3000:
                    output = output[:3000] + "\n... (truncated)"
                return output if output.strip() else "No WHOIS data returned."
            except FileNotFoundError:
                return "WHOIS command not found. Install: pip install python-whois or system whois."
            except subprocess.TimeoutExpired:
                return "WHOIS lookup timed out."
            except Exception as e:
                return f"WHOIS error: {e}"

        return [dns_lookup, reverse_dns, port_check, whois_lookup]
