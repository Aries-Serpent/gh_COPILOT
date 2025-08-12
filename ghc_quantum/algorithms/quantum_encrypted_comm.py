"""Quantum-encrypted communication algorithm."""

import base64
from typing import Optional

from .base import QuantumAlgorithmBase


class QuantumEncryptedCommunication(QuantumAlgorithmBase):
    """Simulated quantum-encrypted communication algorithm."""

    def __init__(self, key: str | None = None, workspace_path: Optional[str] = None):
        super().__init__(workspace_path)
        self.key = key or "quantum-key"

    def get_algorithm_name(self) -> str:
        return "quantum_encrypted_communication"

    def execute_algorithm(self) -> bool:
        self.logger.info("Establishing quantum-encrypted channel")
        return True

    def _xor(self, text: str) -> bytes:
        key_bytes = self.key.encode("utf-8")
        text_bytes = text.encode("utf-8")
        return bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(text_bytes))

    def encrypt_message(self, message: str) -> str:
        """Return base64-encoded XOR of message with key."""
        return base64.urlsafe_b64encode(self._xor(message)).decode("utf-8")

    def decrypt_message(self, encrypted: str) -> str:
        """Decode and XOR to retrieve original message."""
        data = base64.urlsafe_b64decode(encrypted.encode("utf-8"))
        key_bytes = self.key.encode("utf-8")
        return bytes(
            b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data)
        ).decode("utf-8")
