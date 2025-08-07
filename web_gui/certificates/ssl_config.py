"""SSL context configuration helpers."""

from pathlib import Path
import ssl

from secondary_copilot_validator import SecondaryCopilotValidator


def create_ssl_context(
    cert_file: str,
    key_file: str,
    ca_file: str | None = None,
    validator: SecondaryCopilotValidator | None = None,
) -> ssl.SSLContext:
    """Create an SSL context using certificate and key files.

    Args:
        cert_file: Path to the server certificate file.
        key_file: Path to the private key file.
        ca_file: Optional path to a CA bundle file.

    Returns:
        An initialized :class:`ssl.SSLContext` instance.

    Raises:
        FileNotFoundError: If any supplied file does not exist.
    """
    for path in (cert_file, key_file):
        if not Path(path).exists():
            raise FileNotFoundError(f"File not found: {path}")

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)

    if ca_file:
        if not Path(ca_file).exists():
            raise FileNotFoundError(f"File not found: {ca_file}")
        context.load_verify_locations(cafile=ca_file)

    (validator or SecondaryCopilotValidator()).validate_corrections([cert_file, key_file])
    return context
