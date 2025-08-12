"""Integration utilities for quantum-encrypted communication."""

from ghc_quantum.algorithms import QuantumEncryptedCommunication
from secondary_copilot_validator import SecondaryCopilotValidator


class QuantumSecureChannel:
    """High-level interface for quantum-encrypted message exchange."""

    def __init__(
        self,
        key: str | None = None,
        validator: SecondaryCopilotValidator | None = None,
    ):
        self.engine = QuantumEncryptedCommunication(key)
        self.validator = validator or SecondaryCopilotValidator()

    def transmit(self, payload: str) -> str:
        """Encrypt and immediately decrypt the payload to simulate a secure channel."""
        encrypted = self.engine.encrypt_message(payload)
        decrypted = self.engine.decrypt_message(encrypted)
        self.validator.validate_corrections([decrypted])
        return decrypted
