"""Utilities for managing certificate files.

Steps:
1. Load certificate and private key material from disk.
2. Validate file presence before returning bytes.
3. Provide a placeholder for certificate rotation.
"""
from pathlib import Path

from secondary_copilot_validator import SecondaryCopilotValidator


def load_certificate(
    path: str, validator: SecondaryCopilotValidator | None = None
) -> bytes:
    """Read a certificate file from disk.

    Args:
        path: Path to the certificate file.

    Returns:
        Contents of the certificate file as bytes.

    Raises:
        FileNotFoundError: If the certificate file does not exist.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Certificate not found: {path}")
    data = file_path.read_bytes()
    (validator or SecondaryCopilotValidator()).validate_corrections([path])
    return data


def load_private_key(
    path: str, validator: SecondaryCopilotValidator | None = None
) -> bytes:
    """Read a private key file from disk.

    Args:
        path: Path to the private key file.

    Returns:
        Contents of the key file as bytes.

    Raises:
        FileNotFoundError: If the key file does not exist.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Private key not found: {path}")
    data = file_path.read_bytes()
    (validator or SecondaryCopilotValidator()).validate_corrections([path])
    return data


def rotate_certificate(
    current_cert: str,
    new_cert: str,
    validator: SecondaryCopilotValidator | None = None,
) -> None:
    """Placeholder for rotating certificate files.

    Steps:
        1. Load the new certificate from *new_cert*.
        2. Replace the file at *current_cert* with the new data.
        3. Trigger any service reload required to apply the change.
    """
    (validator or SecondaryCopilotValidator()).validate_corrections([current_cert, new_cert])
    # Placeholder: real implementation would ensure atomic swap and backups.
