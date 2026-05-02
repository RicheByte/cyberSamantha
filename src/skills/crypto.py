"""
Crypto Skill — Hashing, encoding/decoding, and basic cryptographic utilities.

Useful for hash identification, quick checksums, Base64/hex conversions,
and password hash analysis during security assessments.
"""

import hashlib
import base64
import binascii
import re
from typing import List, Callable

from src.skills.base import BaseSkill


class CryptoSkill(BaseSkill):
    name = "crypto"
    description = "Hashing, encoding/decoding, hash identification, and basic crypto utilities"
    version = "1.0"
    tags = ["crypto", "hashing", "encoding", "forensics"]
    compatible_agents = set()  # All agents

    def get_tools(self) -> List[Callable]:

        def hash_text(text: str, algorithm: str = "sha256") -> str:
            """
            Hash a string using the specified algorithm.

            Args:
                text: The text to hash.
                algorithm: Hash algorithm — md5, sha1, sha256, sha512 (default: sha256).
            """
            algo = algorithm.lower().strip()
            supported = {"md5", "sha1", "sha256", "sha512", "sha224", "sha384"}
            if algo not in supported:
                return f"Unsupported algorithm: {algo}. Supported: {', '.join(sorted(supported))}"

            h = hashlib.new(algo)
            h.update(text.encode("utf-8"))
            digest = h.hexdigest()
            return f"{algo.upper()}: {digest}"

        def hash_identify(hash_string: str) -> str:
            """
            Identify the likely hash type based on length and character patterns.

            Args:
                hash_string: The hash string to identify.
            """
            h = hash_string.strip()
            length = len(h)

            candidates = []

            # Check if hex
            is_hex = all(c in "0123456789abcdefABCDEF" for c in h)

            if is_hex:
                if length == 32:
                    candidates.append("MD5")
                    candidates.append("NTLM")
                if length == 40:
                    candidates.append("SHA-1")
                    candidates.append("MySQL 4.x")
                if length == 56:
                    candidates.append("SHA-224")
                if length == 64:
                    candidates.append("SHA-256")
                    candidates.append("GOST R 34.11-94")
                if length == 96:
                    candidates.append("SHA-384")
                if length == 128:
                    candidates.append("SHA-512")
                    candidates.append("Whirlpool")
            
            # bcrypt
            if h.startswith("$2b$") or h.startswith("$2a$") or h.startswith("$2y$"):
                candidates = ["bcrypt"]
            # MD5-crypt
            if h.startswith("$1$"):
                candidates = ["MD5-crypt (Unix)"]
            # SHA-256-crypt
            if h.startswith("$5$"):
                candidates = ["SHA-256-crypt (Unix)"]
            # SHA-512-crypt
            if h.startswith("$6$"):
                candidates = ["SHA-512-crypt (Unix)"]
            # Argon2
            if h.startswith("$argon2"):
                candidates = ["Argon2"]

            if not candidates:
                return f"Unknown hash type. Length: {length}, Is hex: {is_hex}"

            return f"Possible hash types for ({length} chars):\n" + "\n".join(f"  • {c}" for c in candidates)

        def base64_encode(text: str) -> str:
            """
            Base64 encode a string.

            Args:
                text: The text to encode.
            """
            encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
            return f"Base64: {encoded}"

        def base64_decode(encoded_text: str) -> str:
            """
            Base64 decode a string.

            Args:
                encoded_text: The Base64 string to decode.
            """
            try:
                decoded = base64.b64decode(encoded_text.strip()).decode("utf-8", errors="replace")
                return f"Decoded: {decoded}"
            except Exception as e:
                return f"Decode error: {e}"

        def hex_encode(text: str) -> str:
            """
            Convert text to hexadecimal representation.

            Args:
                text: The text to convert.
            """
            hex_str = text.encode("utf-8").hex()
            return f"Hex: {hex_str}"

        def hex_decode(hex_string: str) -> str:
            """
            Convert a hexadecimal string back to text.

            Args:
                hex_string: The hex string to decode.
            """
            try:
                decoded = bytes.fromhex(hex_string.strip()).decode("utf-8", errors="replace")
                return f"Decoded: {decoded}"
            except (ValueError, binascii.Error) as e:
                return f"Hex decode error: {e}"

        return [hash_text, hash_identify, base64_encode, base64_decode, hex_encode, hex_decode]
