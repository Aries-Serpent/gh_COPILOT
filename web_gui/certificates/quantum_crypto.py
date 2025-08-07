"""Quantum-safe cryptographic helpers."""

from hashlib import sha3_256
import secrets


def generate_quantum_safe_key(length: int = 32) -> bytes:
    """Generate a random key for quantum-safe algorithms.

    Args:
        length: Size of the key in bytes. Defaults to 32 bytes.

    Returns:
        Random bytes suitable for use as a symmetric key.
    """
    return secrets.token_bytes(length)


def quantum_safe_hash(data: bytes) -> str:
    """Compute a SHA3-256 hash of *data*.

    Args:
        data: Input data to hash.

    Returns:
        Hexadecimal string representation of the digest.
    """
    return sha3_256(data).hexdigest()
