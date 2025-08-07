"""Quantum-safe cryptographic helpers.

Steps:
1. Generate random keys suitable for symmetric encryption.
2. Hash data with SHA3-256 as a stand-in for post-quantum hashing.
3. Serve as placeholders until full quantum-resistant algorithms are integrated.
"""

from hashlib import sha3_256
import secrets

from secondary_copilot_validator import SecondaryCopilotValidator


def generate_quantum_safe_key(
    length: int = 32, validator: SecondaryCopilotValidator | None = None
) -> bytes:
    """Generate a random key for quantum-safe algorithms.

    Args:
        length: Size of the key in bytes. Defaults to 32 bytes.

    Returns:
        Random bytes suitable for use as a symmetric key.
    """
    key = secrets.token_bytes(length)
    (validator or SecondaryCopilotValidator()).validate_corrections([str(length)])
    return key


def quantum_safe_hash(
    data: bytes, validator: SecondaryCopilotValidator | None = None
) -> str:
    """Compute a SHA3-256 hash of *data*.

    Args:
        data: Input data to hash.

    Returns:
        Hexadecimal string representation of the digest.
    """
    digest = sha3_256(data).hexdigest()
    (validator or SecondaryCopilotValidator()).validate_corrections([digest])
    return digest
