"""Integration utilities for quantum-encrypted communication."""

from quantum.algorithms import QuantumEncryptedCommunication


class QuantumSecureChannel:
    """High-level interface for quantum-encrypted message exchange."""

    def __init__(self, key: str | None = None):
        self.engine = QuantumEncryptedCommunication(key)

    def transmit(self, payload: str) -> str:
        """Encrypt and immediately decrypt the payload to simulate a secure channel."""
        encrypted = self.engine.encrypt_message(payload)
        return self.engine.decrypt_message(encrypted)
